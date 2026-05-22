# app.py
import streamlit as st
from config import Config
from streamlit_option_menu import option_menu
import logging
import database
import calculations


# Initialize project settings and logging at the very start
Config.initialize_project()
logger = logging.getLogger(__name__)

def main():
    # Check if this is the first time the app is loaded in this session
    if "app_initialized" not in st.session_state:
        logger.info("Application started successfully (First load).")
        st.session_state["app_initialized"] = True

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.title("Navigation")
        
        # Modern navigation menu with icons
        page = option_menu(
            menu_title=None,  # No extra header inside the menu box
            options=["Insert Weight", "History & Trends"],
            icons=["plus-circle", "graph-up-arrow"],  # Bootstrap icons
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#ff4b4b", "font-size": "18px"}, # Modern red accent
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eeeeee",
                },
                "nav-link-selected": {"background-color": "#ff4b4b"}, # Highlight color
            }
        )

    # --- MAIN CONTENT WITH MATCH-CASE (SWITCH) ---
    match page:
        case "Insert Weight":
            st.title(Config.APP_TITLE)
            st.write(Config.WELCOME_MESSAGE)

            # Create a form for weight entry
            with st.form(key="weight_input_form"):
                weight_value = st.number_input(
                    label="Enter your today's weight (kg):",
                    min_value=30.0,
                    max_value=200.0,
                    value=75.0,
                    step=0.1,
                )
                submit_button = st.form_submit_button(label="Confirm")

            # Logic when user clicks the Confirm button
            if submit_button:
                try:
                    database.save_weight_entry(weight_value)
                    logger.info(
                        f"Successfully saved weight entry: {weight_value} kg"
                    )
                    st.success(
                        f"Weight {weight_value} kg has been successfully saved!"
                    )
                except Exception as e:
                    logger.error(f"Failed to save weight entry: {str(e)}")
                    st.error("An error occurred while saving your weight.")

        case "History & Trends":
            st.title("History & Trends")

            # 1. Load the data from CSV
            df_entries = database.load_weight_data()

            # 2. Perform calculations
            current_average = calculations.calculate_weekly_average(df_entries)
            df_blocks = calculations.calculate_block_averages(df_entries)

            # 3. Display summary metric
            st.subheader("Summary Metrics")
            st.metric(
                label=f"Rolling Average (Last {Config.AVERAGE_DAYS_WINDOW} days)",
                value=f"{current_average} kg"
                if current_average > 0
                else "No data",
            )

            # 4. Display Weight Trend Chart
            st.subheader("Weight Trend Over Time")
            if not df_entries.empty:
                # We tell Streamlit to use 'Date' for X-axis and 'Weight' for Y-axis
                st.line_chart(data=df_entries, x="Date", y="Weight")
            else:
                st.info("No data available to generate a chart.")


            # 5. Display weekly blocks overview
            st.subheader("Weekly Blocks Overview")
            if not df_blocks.empty:
                st.dataframe(df_blocks, use_container_width=True)
            else:
                st.info("No weekly blocks calculated yet.")

            # 5. Display raw history
            st.subheader("Your Weight History")
            if not df_entries.empty:
                st.dataframe(df_entries, use_container_width=True)
            else:
                st.info(
                    "No weight entries found yet. Go to 'Insert Weight' to add some!"
                )

        case _:
            # Default fallback (safety net)
            st.error("Page not found.")

if __name__ == "__main__":
    main()

