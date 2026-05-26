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
    Colors the 'Weekly Change' cell based on central Config colors.
    """
    val = row["Weekly Change"]
    styles = [""] * len(row)
    change_idx = row.index.get_loc("Weekly Change")
    
    if val != "N/A":
        num_val = float(val)
        if num_val < 0:
            # FIXED: Dynamic styling from Config
            styles[change_idx] = f"background-color: {Config.COLOR_SUCCESS_BG}; color: {Config.COLOR_SUCCESS_TX};"
        elif num_val > 0:
            # FIXED: Dynamic styling from Config
            styles[change_idx] = f"background-color: {Config.COLOR_DANGER_BG}; color: {Config.COLOR_DANGER_TX};"
            
    return styles

def main():
    # Check if this is the first time the app is loaded in this session
    if "app_initialized" not in st.session_state:
        logger.info("Application started successfully (First load).")
        st.session_state["app_initialized"] = True

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.title(Config.SIDEBAR_TITLE)
        
        # Modern navigation menu with icons
        page = option_menu(
            menu_title=None,  # No extra header inside the menu box
            options=[Config.SIDEBAR_TAB1, Config.SIDEBAR_TAB2],
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

            st.markdown("---")
            st.subheader("Data Management")
            st.write("Entered an incorrect value? You can delete the most recent log entry.")

            # Logic Delete Last Entry
            if st.button("🗑️ Delete Last Entry", type="secondary", use_container_width=True):
                try:
                    success = database.delete_last_entry()
                    if success:
                        logger.info("Successfully deleted the last weight entry.")
                        st.success("The last entry has been successfully deleted!")
                        st.rerun()
                    else:
                        st.warning("No data found in the database to delete.")
                except Exception as e:
                    logger.error(f"Failed to delete last weight entry: {str(e)}")
                    st.error("An error occurred while deleting the entry.")

        case "History & Trends":
            st.title(Config.SIDEBAR_TAB2)

            # 1. Load data
            df_entries = database.load_weight_data()
            df_blocks = calculations.calculate_block_averages(df_entries)
            current_average = calculations.calculate_weekly_average(df_entries)
            weekly_delta = calculations.calculate_weekly_delta(df_blocks)

            # 2. Setup structural TABS (S pamäťou, aby ti po kliknutí na Next neprepínalo záložku)
            tabs = st.tabs(
                [
                    Config.TAB_SUMMARY_NAME,
                    Config.TAB_BLOCKS_NAME,
                    Config.TAB_HISTORY_NAME,
                ]
            )

            # --- TAB 1: SUMMARY & GRAPH ONLY ---
            with tabs[0]:
                st.subheader(Config.SUBHEADER1)
                
                # Calculate the 4-week forecast using our new function
                predicted_weight = calculations.calculate_forecast(current_average, df_blocks, weeks_ahead=Config.FORECAST_WEEKS_AHEAD)
                
                # Create two horizontal columns for side-by-side metrics
                col_left, col_right = st.columns(2)
                
                with col_left:
                    delta_value = f"{weekly_delta} kg" if weekly_delta is not None else None
                    st.metric(
                        label=f"Rolling Average (Last {Config.AVERAGE_DAYS_WINDOW} days)",
                        value=f"{current_average} kg" if current_average > 0 else "No data",
                        delta=delta_value,
                        delta_color="inverse"
                    )
                
                with col_right:
                    if predicted_weight is not None:
                        # Calculate total expected change over 4 weeks for the delta label
                        total_predicted_change = round(predicted_weight - current_average, 2)
                        delta_forecast = f"{total_predicted_change:+.2f} kg"
                        
                        st.metric(
                            label=f"Forecast (In {Config.FORECAST_WEEKS_AHEAD} Weeks)",
                            value=f"{predicted_weight} kg",
                            delta=delta_forecast,
                            delta_color="inverse" # Keeps weight loss green, gain red
                        )
                    else:
                        st.metric(
                            label=f"Forecast (In {Config.FORECAST_WEEKS_AHEAD} Weeks)",
                            value="Need more data",
                            help="We need at least 2 consecutive weeks with data to predict your trend."
                        )
                
                st.markdown("---")
                st.subheader(Config.SUBHEADER2)
                if not df_entries.empty:
                    df_chart = df_entries.copy()
                    df_chart["Date"] = df_chart["Date"].astype(str)
                    st.line_chart(data=df_chart, x="Date", y="Weight")
                else:
                    st.info("No data available to generate a chart.")

            # --- TAB 2: WEEKLY BLOCKS ONLY ---
            with tabs[1]:
                st.subheader(Config.SUBHEADER3)
                if not df_blocks.empty:
                    df_blocks_display = df_blocks.copy()
                    df_blocks_display.index = df_blocks_display.index + 1
                    
                    styled_df = df_blocks_display.style.apply(style_weekly_change, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No weekly blocks calculated yet.")

            # --- TAB 3: HISTORY LOG WITH PAGES (PAGINATION) ---
            with tabs[2]:
                st.subheader(Config.SUBHEADER4)
                
                if not df_entries.empty:
                    # Sort data Descendingly
                    df_history_sorted = df_entries.sort_values(by="Date", ascending=False).reset_index(drop=True)
                    
                    ROWS_PER_PAGE = Config.PAGINATION_ROWS_PER_PAGE
                    
                    if "current_page" not in st.session_state:
                        st.session_state.current_page = 0
                        
                    total_rows = len(df_history_sorted)
                    max_pages = (total_rows - 1) // ROWS_PER_PAGE + 1
                    
                    start_idx = st.session_state.current_page * ROWS_PER_PAGE
                    end_idx = start_idx + ROWS_PER_PAGE
                    
                    # Cut fromm sorted data
                    df_page = df_history_sorted.iloc[start_idx:end_idx]
                    
                    # Hide index and show
                    st.dataframe(df_page, use_container_width=True, hide_index=True)
                    
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

