"""
多语言SEO意图探索工具
主应用程序文件
"""

import streamlit as st
import pandas as pd
from utils import get_keywords, MARKET_CONFIG, TRANSLATIONS

# 初始化session state
if 'interface_lang' not in st.session_state:
    st.session_state.interface_lang = "Chinese"

# 获取翻译字典（用于页面配置）
t_init = TRANSLATIONS[st.session_state.interface_lang]

# 设置页面配置（必须在侧边栏之前）
st.set_page_config(
    page_title=t_init["page_title"],
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 侧边栏配置
with st.sidebar:
    # 语言选择器（放在最顶部）
    interface_lang = st.selectbox(
        "Interface Language / 界面语言",
        options=["Chinese", "English"],
        index=0 if st.session_state.interface_lang == "Chinese" else 1,
        key="lang_selector"
    )
    
    # 更新session state
    st.session_state.interface_lang = interface_lang
    
    # 获取翻译字典
    t = TRANSLATIONS[interface_lang]
    
    st.markdown("---")
    st.header(t["sidebar_header"])
    
    # API密钥输入（密码类型）
    api_key = st.text_input(
        t["api_key_label"],
        type="password",
        help=t["api_key_help"],
        placeholder=t["api_key_placeholder"]
    )
    
    # 添加获取API密钥的链接
    st.markdown(t["api_key_link"])
    
    st.markdown("---")
    
    # 多选目标市场
    available_markets = list(MARKET_CONFIG.keys())
    default_markets = ["Germany", "United States"] if "Germany" in available_markets and "United States" in available_markets else available_markets[:2] if len(available_markets) >= 2 else available_markets
    
    selected_markets = st.multiselect(
        t["select_markets_label"],
        options=available_markets,
        default=default_markets,
        help=t["select_markets_help"]
    )
    
    st.markdown("---")
    st.markdown(t["instructions_title"])
    st.markdown(t["instructions"])

# 获取翻译字典（用于主界面）
t = TRANSLATIONS[st.session_state.interface_lang]

# 页面标题
st.title(f"🌍 {t['title']}")
st.markdown("---")
st.markdown(f"### {t['subtitle']}")

# 主界面
st.markdown(t["keyword_gen_title"])

# 文本输入：英文种子关键词
seed_keyword = st.text_input(
    t["seed_keyword_label"],
    placeholder=t["seed_keyword_placeholder"],
    help=t["seed_keyword_help"]
)

# 生成按钮
generate_button = st.button(
    t["generate_btn"],
    type="primary",
    use_container_width=True
)

# 处理按钮点击事件
if generate_button:
    if not seed_keyword or not seed_keyword.strip():
        st.error(t["error_no_keyword"])
    elif not selected_markets:
        st.error(t["error_no_market"])
    else:
        # 初始化结果列表
        all_results = []
        all_market_insights = []
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_markets = len(selected_markets)
        
        try:
            # 循环处理每个选中的市场
            for idx, country in enumerate(selected_markets):
                # 获取对应的语言
                language = MARKET_CONFIG.get(country, "English")
                
                # 更新进度条和状态
                progress = (idx + 1) / total_markets
                progress_bar.progress(progress)
                status_text.text(t["processing_status"].format(
                    country=country,
                    language=language,
                    current=idx + 1,
                    total=total_markets
                ))
                
                # 调用工具函数获取关键词
                result = get_keywords(
                    api_key=api_key,
                    seed_keyword=seed_keyword.strip(),
                    target_language=language,
                    target_country=country,
                    interface_lang=st.session_state.interface_lang
                )
                
                # 保存市场洞察
                market_insight = result.get("market_insight", "")
                all_market_insights.append({
                    "country": country,
                    "language": language,
                    "insight": market_insight
                })
                
                # 处理关键词列表，添加国家列
                keywords_list = result.get("keywords", [])
                for kw in keywords_list:
                    kw_with_country = {
                        "Country": country,
                        t["col_keyword"]: kw.get("native_term", ""),
                        t["col_translation"]: kw.get("english_translation", ""),
                        t["col_intent"]: kw.get("intent_type", ""),
                        t["col_hotness"]: kw.get("popularity_score", 50),
                        t["col_reason"]: kw.get("rationale", "")
                    }
                    all_results.append(kw_with_country)
            
            # 完成进度条
            progress_bar.progress(1.0)
            status_text.text(t["processing_complete"])
            
            # 显示市场洞察摘要
            st.markdown("---")
            st.markdown(t["market_insights_title"])
            for insight_info in all_market_insights:
                with st.expander(f"📊 {insight_info['country']} ({insight_info['language']})"):
                    st.info(insight_info['insight'])
            
            # 合并所有结果到一个DataFrame
            if all_results:
                st.markdown(t["keywords_list_title"])
                
                df = pd.DataFrame(all_results)
                
                # 按AI Hotness降序排序（流行度高的排在前面）
                df = df.sort_values(by=t["col_hotness"], ascending=False)
                
                # 重新排列列顺序，将Country放在最前面
                column_order = ["Country", t["col_keyword"], t["col_translation"], t["col_intent"], t["col_hotness"], t["col_reason"]]
                df = df[column_order]
                
                # 重置索引
                df = df.reset_index(drop=True)
                
                # 添加序号列
                df.insert(0, t["col_序号"], range(1, len(df) + 1))
                
                # 显示说明信息
                st.caption(t["hotness_caption"])
                
                # 显示表格
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        t["col_hotness"]: st.column_config.NumberColumn(
                            t["col_hotness"],
                            help=t["hotness_help"],
                            min_value=0,
                            max_value=100,
                            format="%d"
                        )
                    }
                )
                
                # 显示统计信息
                st.markdown(t["total_stats"].format(count=len(df), markets=len(selected_markets)))
                
                # 添加下载按钮
                csv = df.to_csv(index=False).encode('utf-8-sig')
                countries_str = "_".join(selected_markets[:3])  # 限制文件名长度
                if len(selected_markets) > 3:
                    countries_str += f"_and_{len(selected_markets)-3}_more"
                st.download_button(
                    label=t["download_btn"],
                    data=csv,
                    file_name=f"{seed_keyword}_{countries_str}_keywords.csv",
                    mime="text/csv"
                )
            else:
                st.warning(t["warning_no_keywords"])
            
            # 清除进度条和状态文本
            progress_bar.empty()
            status_text.empty()
                    
        except ValueError as e:
            st.error(t["error_format"].format(error=str(e)))
            progress_bar.empty()
            status_text.empty()
        except Exception as e:
            st.error(t["error_generate"].format(error=str(e)))
            st.info(t["info_error_help"])
            progress_bar.empty()
            status_text.empty()

# 页面底部的说明
st.markdown("---")
with st.expander(t["about_title"]):
    st.markdown(t["about_content"])
