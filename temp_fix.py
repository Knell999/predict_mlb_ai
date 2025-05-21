        # Add metrics description text based on language
        if lang == "en":
            st.markdown("""
            ### 2. Analysis Metrics
            - **Batting Average**
            - **On-Base Percentage**
            - **Slugging Percentage**
            - **OPS (On-base + Slugging)**
            - **Hits**
            - **RBIs**
            - **Home Runs**
            - **Stolen Bases**
            - **Walks**
            - **Strikeouts**

            ### 3. Key Metrics Analysis and Meaning
            """)
        elif lang == "ja":
            st.markdown("""
            ### 2. 分析指標
            - **打率**
            - **出塁率**
            - **長打率**
            - **OPS (出塁率 + 長打率)**
            - **ヒット**
            - **打点**
            - **ホームラン**
            - **盗塁**
            - **四球**
            - **三振**

            ### 3. 主要指標分析と意味
            """)
        else:  # Default to Korean
            st.markdown("""
            ### 2. 분석 지표
            - **Batting Average (타율)**
            - **On-Base Percentage (출루율)**
            - **Slugging Percentage (장타율)**
            - **OPS (출루율 + 장타율)**
            - **Hits (안타)**
            - **RBIs (타점)**
            - **Home Runs (홈런)**
            - **Stolen Bases (도루)**
            - **Walks (볼넷)**
            - **Strikeouts (삼진)**

            ### 3. 주요 지표 분석 및 의미
            """)
