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

def style_weekly_change(row):
    """
    CSS styling function for Streamlit dataframe.
    Colors the 'Weekly Change' cell light green if negative, light red if positive.
    """
    val = row["Weekly Change"]
    
    # Default styling for the row (no background color)
    styles = [""] * len(row)
    
    # Find the index of the 'Weekly Change' column in the row
    change_idx = row.index.get_loc("Weekly Change")
    
    # Apply color based on the value
    if val != "N/A":
        num_val = float(val)
        if num_val < 0:
            styles[change_idx] = "background-color: #d4edda; color: #155724;"  # Light Green
        elif num_val > 0:
            styles[change_idx] = "background-color: #f8d7da; color: #721c24;"  # Light Red
            
    return styles

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

            # 1. Load data
            df_entries = database.load_weight_data()
            df_blocks = calculations.calculate_block_averages(df_entries)
            current_average = calculations.calculate_weekly_average(df_entries)
            weekly_delta = calculations.calculate_weekly_delta(df_blocks)

            # 2. Setup structural TABS (S pamäťou, aby ti po kliknutí na Next neprepínalo záložku)
            tabs = st.tabs(["📊 Summary & Trend", "🧱 Weekly Blocks", "📜 Full History Log"])

            # --- TAB 1: SUMMARY & GRAPH ONLY ---
            with tabs[0]:
                st.subheader("Current Overview")
                delta_value = f"{weekly_delta} kg" if weekly_delta is not None else None
                st.metric(
                    label=f"Rolling Average (Last {Config.AVERAGE_DAYS_WINDOW} days)",
                    value=f"{current_average} kg" if current_average > 0 else "No data",
                    delta=delta_value,
                    delta_color="inverse"
                )
                
                st.markdown("---")
                st.subheader("Weight Trend Chart")
                if not df_entries.empty:
                    st.line_chart(data=df_entries, x="Date", y="Weight")
                else:
                    st.info("No data available to generate a chart.")

            # --- TAB 2: WEEKLY BLOCKS ONLY ---
            with tabs[1]:
                st.subheader("Weekly Blocks Overview")
                if not df_blocks.empty:
                    df_blocks_display = df_blocks.copy()
                    df_blocks_display.index = df_blocks_display.index + 1
                    
                    styled_df = df_blocks_display.style.apply(style_weekly_change, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No weekly blocks calculated yet.")

            # --- TAB 3: HISTORY LOG WITH PAGES (PAGINATION) ---
            with tabs[2]:
                st.subheader("Complete History Log")
                
                if not df_entries.empty:
                    ROWS_PER_PAGE = 10
                    
                    if "current_page" not in st.session_state:
                        st.session_state.current_page = 0
                        
                    total_rows = len(df_entries)
                    max_pages = (total_rows - 1) // ROWS_PER_PAGE + 1
                    
                    start_idx = st.session_state.current_page * ROWS_PER_PAGE
                    end_idx = start_idx + ROWS_PER_PAGE
                    df_page = df_entries.iloc[start_idx:end_idx]
                    
                    # Show only first page (10 rows)
                    df_page_display = df_page.copy()
                    df_page_display.index = df_page_display.index + 1
                    st.dataframe(df_page_display, use_container_width=True)
                    
                    # Control buttons
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if st.button("⬅️ Previous") and st.session_state.current_page > 0:
                            st.session_state.current_page -= 1
                            st.rerun()
                            
                    with col2:
                        st.markdown(
                            f"<p style='text-align: center; color: gray; padding-top: 5px;'>"
                            f"Page {st.session_state.current_page + 1} of {max_pages} ({total_rows} entries)"
                            f"</p>", 
                            unsafe_allow_html=True
                        )
                        
                    with col3:
                        if st.button("Next ➡️") and st.session_state.current_page < max_pages - 1:
                            st.session_state.current_page += 1
                            st.rerun()
                else:
                    st.info("No weight entries found yet.")

            
        case _:
            # Default fallback (safety net)
            st.error("Page not found.")

if __name__ == "__main__":
    main()

