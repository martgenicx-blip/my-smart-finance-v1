# --- History Log එකේම Delete Button එක දාපු අලුත් ක්‍රමය ---

with tab2: # History Log Tab එක ඇතුළේ
    if not df.empty:
        st.subheader("පරණ දත්ත සහ මකා දැමීම")
        
        # දත්ත ටික අන්තිමට දාපු එක උඩට එන විදිහට සකසමු
        display_df = df.copy()
        display_df['Row ID'] = range(2, len(df) + 2)
        display_df = display_df.iloc[::-1] # Reverse history

        for index, row in display_df.iterrows():
            # හැම පේළියකටම Columns 5ක් හදමු දත්ත සහ බොත්තම පෙන්වන්න
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
            
            c1.write(row['Date'])
            c2.write(row['Category'])
            c3.write(f"LKR {row['Amount']}")
            c4.write(row['Description'])
            
            # Delete Button එක
            if c5.button("🗑️", key=f"del_{row['Row ID']}"):
                worksheet.delete_rows(int(row['Row ID']))
                st.warning(f"Row {row['Row ID']} මකා දැමුවා!")
                st.rerun()
            st.divider() # පේළි අතර වෙන් කිරීමක්
    else:
        st.info("දත්ත කිසිවක් නැත.")
