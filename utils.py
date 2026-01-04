"""
工具函数模块
处理DeepSeek API调用和JSON解析（通过OpenAI SDK）
"""

import json
from typing import Dict, List, Optional
from openai import OpenAI

# 国际化翻译字典
TRANSLATIONS = {
    "Chinese": {
        "page_title": "多语言SEO意图探索工具",
        "title": "多语言SEO意图探索工具",
        "subtitle": "帮助SEO专家通过AI分析找到高意图的本地化关键词",
        "sidebar_header": "⚙️ 配置设置",
        "api_key_label": "DeepSeek API密钥",
        "api_key_help": "输入您的DeepSeek API密钥。如果留空，将使用模拟数据（不会消耗API配额）",
        "api_key_placeholder": "输入您的API密钥",
        "api_key_link": "[🔑 获取DeepSeek API密钥](https://platform.deepseek.com)",
        "select_markets_label": "选择目标市场",
        "select_markets_help": "可以选择多个目标市场进行批量处理",
        "instructions_title": "### 📝 使用说明",
        "instructions": """
    1. 输入DeepSeek API密钥（可选，留空使用模拟数据）
    2. 选择一个或多个目标市场
    3. 在主界面输入英文种子关键词
    4. 点击"生成本地化关键词"按钮
    5. 查看所有选中市场的关键词列表（按AI Hotness排序）
    """,
        "keyword_gen_title": "### 📊 关键词生成",
        "seed_keyword_label": "输入英文种子关键词",
        "seed_keyword_placeholder": "例如：Robot Lawn Mower",
        "seed_keyword_help": "输入您想要本地化的英文关键词",
        "generate_btn": "🚀 生成本地化关键词",
        "error_no_keyword": "❌ 请输入英文种子关键词！",
        "error_no_market": "❌ 请至少选择一个目标市场！",
        "processing_status": "正在处理 {country} ({language})... ({current}/{total})",
        "processing_complete": "✅ 所有市场处理完成！",
        "market_insights_title": "### 💡 市场洞察摘要",
        "keywords_list_title": "### 📋 本地化关键词列表（所有市场）",
        "col_序号": "序号",
        "col_country": "Country",
        "col_keyword": "本地关键词",
        "col_translation": "英文翻译",
        "col_intent": "意图类型",
        "col_hotness": "AI Hotness",
        "col_reason": "选择理由",
        "hotness_caption": "💡 **AI Hotness**：这是基于AI训练数据估算的相对流行度分数（0-100），不是真实的Google搜索数据。分数越高表示该关键词在该市场可能越常见。",
        "hotness_help": "基于AI训练数据估算的相对流行度分数（0-100），不是真实的Google搜索数据",
        "total_stats": "**总计**：{count} 个关键词，覆盖 {markets} 个市场",
        "download_btn": "📥 下载为CSV文件（包含所有市场）",
        "warning_no_keywords": "⚠️ 未生成任何关键词，请检查API响应格式",
        "error_format": "❌ 数据格式错误：{error}",
        "error_generate": "❌ 生成关键词时出错：{error}",
        "info_error_help": "💡 提示：如果没有输入API密钥，将自动使用模拟数据。如果输入了API密钥仍出现错误，请检查密钥是否正确。您可以在侧边栏点击链接获取API密钥。",
        "about_title": "ℹ️ 关于此工具",
        "about_content": """
    **多语言SEO意图探索工具**
    
    这个工具使用AI（DeepSeek模型）来帮助SEO专家：
    - 🔍 分析英文关键词在目标市场的搜索意图
    - 🌐 生成本地化关键词（而非直接翻译）
    - 📊 识别不同意图类型的关键词（主要词、同义词、长尾词）
    - 💡 提供市场洞察和关键词选择理由
    
    **工作原理：**
    1. 您输入一个英文种子关键词
    2. AI分析该关键词在目标市场的搜索意图
    3. 基于搜索意图和本地习惯，生成相关关键词
    4. 返回结构化数据，包括市场洞察和关键词列表
    
    **使用建议：**
    - 如果没有API密钥，可以先用模拟数据测试界面功能
    - 输入API密钥后，将使用真实的AI模型生成结果
    - 生成的关键词可以导出为CSV文件，方便后续分析
    """,
    },
    "English": {
        "page_title": "Multi-Language SEO Intent Explorer",
        "title": "Multi-Language SEO Intent Explorer",
        "subtitle": "Help SEO experts find high-intent localized keywords through AI analysis",
        "sidebar_header": "⚙️ Configuration",
        "api_key_label": "DeepSeek API Key",
        "api_key_help": "Enter your DeepSeek API key. Leave empty to use mock data (no API quota consumed)",
        "api_key_placeholder": "Enter your API key",
        "api_key_link": "[🔑 Get DeepSeek API Key](https://platform.deepseek.com)",
        "select_markets_label": "Select Target Markets",
        "select_markets_help": "You can select multiple target markets for batch processing",
        "instructions_title": "### 📝 Instructions",
        "instructions": """
    1. Enter DeepSeek API key (optional, leave empty to use mock data)
    2. Select one or more target markets
    3. Enter an English seed keyword in the main interface
    4. Click the "Generate Localized Keywords" button
    5. View the keyword list for all selected markets (sorted by AI Hotness)
    """,
        "keyword_gen_title": "### 📊 Keyword Generation",
        "seed_keyword_label": "Enter English Seed Keyword",
        "seed_keyword_placeholder": "e.g., Robot Lawn Mower",
        "seed_keyword_help": "Enter the English keyword you want to localize",
        "generate_btn": "🚀 Generate Localized Keywords",
        "error_no_keyword": "❌ Please enter an English seed keyword!",
        "error_no_market": "❌ Please select at least one target market!",
        "processing_status": "Processing {country} ({language})... ({current}/{total})",
        "processing_complete": "✅ All markets processed!",
        "market_insights_title": "### 💡 Market Insights Summary",
        "keywords_list_title": "### 📋 Localized Keywords List (All Markets)",
        "col_序号": "No.",
        "col_country": "Country",
        "col_keyword": "Local Keyword",
        "col_translation": "English Translation",
        "col_intent": "Intent Type",
        "col_hotness": "AI Hotness",
        "col_reason": "Reasoning",
        "hotness_caption": "💡 **AI Hotness**: This is an AI-estimated relative popularity score (0-100) based on training data, not real Google search data. Higher scores indicate the keyword may be more common in that market.",
        "hotness_help": "AI-estimated relative popularity score (0-100) based on training data, not real Google search data",
        "total_stats": "**Total**: {count} keywords covering {markets} markets",
        "download_btn": "📥 Download as CSV (All Markets)",
        "warning_no_keywords": "⚠️ No keywords generated. Please check API response format.",
        "error_format": "❌ Data format error: {error}",
        "error_generate": "❌ Error generating keywords: {error}",
        "info_error_help": "💡 Tip: If no API key is entered, mock data will be used automatically. If you entered an API key and still see errors, please check if the key is correct. You can click the link in the sidebar to get an API key.",
        "about_title": "ℹ️ About This Tool",
        "about_content": """
    **Multi-Language SEO Intent Explorer**
    
    This tool uses AI (DeepSeek model) to help SEO experts:
    - 🔍 Analyze search intent of English keywords in target markets
    - 🌐 Generate localized keywords (not direct translations)
    - 📊 Identify different intent types of keywords (primary, synonym, long-tail)
    - 💡 Provide market insights and keyword selection reasoning
    
    **How It Works:**
    1. You enter an English seed keyword
    2. AI analyzes the search intent of this keyword in target markets
    3. Based on search intent and local habits, generates relevant keywords
    4. Returns structured data including market insights and keyword lists
    
    **Usage Tips:**
    - If you don't have an API key, you can test the interface with mock data first
    - After entering an API key, the real AI model will be used to generate results
    - Generated keywords can be exported as CSV files for further analysis
    """,
    }
}

# 市场配置字典：映射国家到语言
MARKET_CONFIG = {
    "Germany": "German",
    "United States": "English",
    "France": "French",
    "Italy": "Italian",
    "Spain": "Spanish",
    "China": "Chinese",
    "Japan": "Japanese",
    "South Korea": "Korean",
    "Brazil": "Portuguese",
    "Netherlands": "Dutch",
    "United Kingdom": "English",
    "Canada": "English",
    "Australia": "English",
    "India": "English",
    "Russia": "Russian",
    "Mexico": "Spanish",
    "Argentina": "Spanish",
    "Poland": "Polish",
    "Turkey": "Turkish",
    "Sweden": "Swedish",
    "Norway": "Norwegian",
    "Denmark": "Danish",
    "Finland": "Finnish",
    "Belgium": "French",
    "Switzerland": "German",
    "Austria": "German",
    "Portugal": "Portuguese",
    "Greece": "Greek",
    "Czech Republic": "Czech",
    "Hungary": "Hungarian",
    "Romania": "Romanian",
    "Israel": "Hebrew",
    "South Africa": "English",
    "New Zealand": "English",
    "Singapore": "English",
    "Malaysia": "Malay",
    "Thailand": "Thai",
    "Indonesia": "Indonesian",
    "Philippines": "Filipino",
    "Vietnam": "Vietnamese",
    "Chile": "Spanish",
    "Colombia": "Spanish",
    "Peru": "Spanish",
    "Venezuela": "Spanish",
    "Egypt": "Arabic",
    "Saudi Arabia": "Arabic",
    "United Arab Emirates": "Arabic",
    "Qatar": "Arabic",
    "Kuwait": "Arabic",
    "Ireland": "English",
    "Ukraine": "Ukrainian",
    "Belarus": "Belarusian",
    "Kazakhstan": "Kazakh",
    "Uzbekistan": "Uzbek",
    "Pakistan": "Urdu",
    "Bangladesh": "Bengali",
    "Sri Lanka": "Sinhala",
    "Nepal": "Nepali",
    "Myanmar": "Burmese",
    "Cambodia": "Khmer",
    "Laos": "Lao",
    "Mongolia": "Mongolian",
    "Brunei": "Malay",
    "East Timor": "Tetum",
    "Afghanistan": "Pashto",
    "Iraq": "Arabic",
    "Iran": "Persian",
    "Jordan": "Arabic",
    "Lebanon": "Arabic",
    "Syria": "Arabic",
    "Yemen": "Arabic",
    "Oman": "Arabic",
    "Bahrain": "Arabic",
    "Morocco": "Arabic",
    "Algeria": "Arabic",
    "Tunisia": "Arabic",
    "Libya": "Arabic",
    "Sudan": "Arabic",
    "Ethiopia": "Amharic",
    "Kenya": "Swahili",
    "Tanzania": "Swahili",
    "Uganda": "English",
    "Ghana": "English",
    "Nigeria": "English",
    "Cameroon": "French",
    "Ivory Coast": "French",
    "Senegal": "French",
    "Mali": "French",
    "Burkina Faso": "French",
    "Niger": "French",
    "Chad": "French",
    "Central African Republic": "French",
    "Democratic Republic of the Congo": "French",
    "Republic of the Congo": "French",
    "Gabon": "French",
    "Equatorial Guinea": "Spanish",
    "São Tomé and Príncipe": "Portuguese",
    "Angola": "Portuguese",
    "Zambia": "English",
    "Zimbabwe": "English",
    "Botswana": "English",
    "Namibia": "English",
    "Mozambique": "Portuguese",
    "Madagascar": "Malagasy",
    "Mauritius": "English",
    "Seychelles": "English",
    "Comoros": "Comorian",
    "Djibouti": "French",
    "Eritrea": "Tigrinya",
    "Somalia": "Somali",
    "Rwanda": "Kinyarwanda",
    "Burundi": "Kirundi",
    "Malawi": "English",
    "Lesotho": "Sesotho",
    "Eswatini": "English",
    "Guinea": "French",
    "Guinea-Bissau": "Portuguese",
    "Sierra Leone": "English",
    "Liberia": "English",
    "Togo": "French",
    "Benin": "French",
    "Mauritania": "Arabic",
    "Gambia": "English",
    "Cape Verde": "Portuguese",
}


def get_mock_response(keyword: str, target_language: str, target_country: str) -> Dict:
    """
    生成模拟数据（当没有API密钥时使用）
    这个函数返回一个模拟的JSON响应，用于测试UI而无需消耗API配额
    """
    mock_data = {
        "market_insight": f"在{target_country}市场，'{keyword}'相关的搜索意图主要集中在自主维护设备、智能家居解决方案和可持续生活方式。本地消费者更倾向于使用长尾关键词，并且对产品规格和技术细节的搜索兴趣较高。",
        "keywords": [
            {
                "native_term": "Rasenmähroboter",
                "english_translation": "Robot lawn mower",
                "intent_type": "Primary",
                "rationale": "这是德语市场中最常用的搜索词，直接对应产品类别",
                "popularity_score": 95
            },
            {
                "native_term": "automatischer Rasenmäher",
                "english_translation": "Automatic lawn mower",
                "intent_type": "Synonym",
                "rationale": "同义词变体，搜索量较低但相关性强",
                "popularity_score": 65
            },
            {
                "native_term": "bester Rasenmähroboter 2024",
                "english_translation": "Best robot lawn mower 2024",
                "intent_type": "Long-tail",
                "rationale": "高购买意图的长尾关键词，包含年份和比较意图",
                "popularity_score": 75
            },
            {
                "native_term": "Rasenmähroboter Test",
                "english_translation": "Robot lawn mower test/review",
                "intent_type": "Long-tail",
                "rationale": "信息意图关键词，用户正在研究产品评测",
                "popularity_score": 70
            },
            {
                "native_term": "Mähroboter kaufen",
                "english_translation": "Buy robot lawn mower",
                "intent_type": "Long-tail",
                "rationale": "明确的交易意图关键词，包含购买行为词",
                "popularity_score": 80
            }
        ]
    }
    return mock_data


def generate_localized_keywords(
    api_key: str,
    seed_keyword: str,
    target_language: str,
    target_country: str,
    interface_lang: str = "Chinese"
) -> Dict:
    """
    调用DeepSeek API生成本地化关键词（通过OpenAI SDK）
    
    参数:
        api_key: DeepSeek API密钥
        seed_keyword: 英文种子关键词
        target_language: 目标语言
        target_country: 目标国家
    
    返回:
        包含市场洞察和关键词列表的字典
    """
    # 初始化DeepSeek客户端（使用OpenAI兼容的API）
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    # 系统提示词：指导LLM作为本地SEO专家，返回严格JSON格式
    # 确定界面语言描述
    interface_lang_desc = "English" if interface_lang == "English" else "Chinese"
    
    system_prompt = f"""You are an experienced local SEO specialist focusing on search intent and keyword strategies in target markets.

Your tasks are:
1. Analyze the search intent of English seed keywords in target markets
2. Generate localized keywords, not direct translations
3. Consider local consumer search habits, language conventions, and cultural background
4. Estimate the relative popularity of each keyword (based on your training data knowledge)
5. Return a response in strict JSON format

Required JSON format:
{{
  "market_insight": "A summary of the local market search landscape (in {interface_lang_desc})",
  "keywords": [
    {{
      "native_term": "Local keyword (in target language)",
      "english_translation": "English translation",
      "intent_type": "Primary" | "Synonym" | "Long-tail",
      "rationale": "Explanation of why this keyword was chosen (in {interface_lang_desc})",
      "popularity_score": integer (0-100)
    }}
  ]
}}

Important rules:
- intent_type must be one of: "Primary", "Synonym", or "Long-tail"
- Generate 5-8 high-quality keywords
- Consider different search intents: purchase intent, informational intent, navigational intent, etc.
- Do not directly translate; generate keywords based on search intent and local habits
- **popularity_score rules**:
  * popularity_score must be an integer from 0 to 100
  * 100 = Extremely common head term (e.g., "Rasenmähroboter" in the German market should score 90-100)
  * 80-99 = Very popular keywords
  * 60-79 = Moderately popular keywords
  * 40-59 = Less used keywords
  * 0-39 = Very rare long-tail keywords
  * You must estimate this score based on knowledge from your training data; common head terms should score high, long-tail specific queries should score low
- **CRITICAL: Output the 'market_insight' and 'rationale' fields strictly in {interface_lang_desc}. For example, if the interface language is English, explain the German keywords using English.**
- **Important: Must return raw JSON string, do not use Markdown code block format (do not use ```json markers), return JSON object directly**"""
    
    user_prompt = f"""Generate localized keywords for the following English seed keyword in the {target_country} ({target_language}) market:

Seed keyword: {seed_keyword}

Target market: {target_country}
Target language: {target_language}

Generate keywords based on search intent (not direct translation) and estimate popularity_score for each keyword (based on your training data knowledge). Return results in pure JSON format (do not use Markdown format). All explanations must be in {interface_lang_desc}."""
    
    try:
        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},  # 强制返回JSON格式
            temperature=0.7
        )
        
        # 解析JSON响应
        response_text = response.choices[0].message.content
        result = json.loads(response_text)
        
        # 验证返回的数据结构
        if "market_insight" not in result or "keywords" not in result:
            raise ValueError("API返回的JSON格式不正确，缺少必要字段")
        
        # 验证每个关键词都有popularity_score字段
        for kw in result.get("keywords", []):
            if "popularity_score" not in kw:
                # 如果没有提供，设置默认值
                kw["popularity_score"] = 50
            else:
                # 确保popularity_score在0-100范围内
                kw["popularity_score"] = max(0, min(100, int(kw.get("popularity_score", 50))))
        
        return result
        
    except json.JSONDecodeError as e:
        error_msg = f"无法解析API返回的JSON：{str(e)}"
        try:
            error_msg += f"。原始响应：{response_text[:200]}"
        except NameError:
            pass
        raise ValueError(error_msg)
    except Exception as e:
        raise Exception(f"API调用失败：{str(e)}")


def get_keywords(
    api_key: Optional[str],
    seed_keyword: str,
    target_language: str,
    target_country: str,
    interface_lang: str = "Chinese"
) -> Dict:
    """
    获取本地化关键词的主函数
    如果提供了API密钥，调用真实API；否则返回模拟数据
    
    参数:
        api_key: DeepSeek API密钥（可选）
        seed_keyword: 英文种子关键词
        target_language: 目标语言
        target_country: 目标国家
    
    返回:
        包含市场洞察和关键词列表的字典
    """
    if api_key and api_key.strip():
        # 使用真实API
        try:
            return generate_localized_keywords(
                api_key=api_key,
                seed_keyword=seed_keyword,
                target_language=target_language,
                target_country=target_country,
                interface_lang=interface_lang
            )
        except Exception as e:
            raise e
    else:
        # 使用模拟数据
        return get_mock_response(
            keyword=seed_keyword,
            target_language=target_language,
            target_country=target_country
        )
