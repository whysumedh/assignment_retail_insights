"""
Prompt engineering layer for consistent and accurate responses.
Contains system prompts, context-aware prompts, and few-shot examples.
"""

from typing import Dict, List, Optional


class PromptEngine:
    """Prompt engineering class for generating consistent prompts."""
    
    SYSTEM_PROMPT = """You are a Retail Insights Assistant, an expert AI assistant specialized in analyzing retail pricing data and answering business questions about e-commerce platforms, product pricing, and market insights.

Your role:
- Answer questions about product pricing across different e-commerce platforms (Ajio, Amazon, Flipkart, Myntra, etc.)
- Provide insights about price comparisons, cheapest platforms, and pricing trends
- Help users make informed purchasing decisions
- Analyze product categories, catalogs, and pricing patterns

Guidelines:
- Always base your answers on the provided data
- Be precise with numbers and prices
- If data is not available, clearly state that
- Use Indian Rupees (₹) for all price references
- Provide actionable insights when possible
- Be concise but thorough
"""

    FEW_SHOT_EXAMPLES = [
        {
            "question": "Which e-commerce site is relatively cheaper to buy kurtas?",
            "answer": "Based on the data, I analyzed kurta prices across all platforms. [Platform X] offers the lowest average price of ₹[amount] for kurtas, making it the most cost-effective option. However, prices may vary by specific style, so I recommend checking individual products."
        },
        {
            "question": "What is the price range for products in the Moments catalog?",
            "answer": "The Moments catalog has products ranging from ₹[min] to ₹[max], with an average price of ₹[avg]. This catalog contains [count] products across [categories] categories."
        },
        {
            "question": "Show me the cheapest platform for style Os206_3141",
            "answer": "For style Os206_3141, the cheapest platform is [Platform] at ₹[price]. All sizes (S, M, L, XL, 2XL, 3XL) are available at this price."
        }
    ]
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for the assistant."""
        return PromptEngine.SYSTEM_PROMPT
    
    @staticmethod
    def build_question_prompt(
        user_question: str,
        context_data: Optional[str] = None,
        relevant_products: Optional[List[Dict]] = None
    ) -> str:
        """
        Build a prompt for answering user questions.
        
        Args:
            user_question: The user's question
            context_data: Optional context data (summary statistics, etc.)
            relevant_products: Optional list of relevant product dictionaries
            
        Returns:
            Formatted prompt string
        """
        prompt = f"{PromptEngine.SYSTEM_PROMPT}\n\n"
        
        # Add few-shot examples
        prompt += "Example Questions and Answers:\n"
        for example in PromptEngine.FEW_SHOT_EXAMPLES:
            prompt += f"\nQ: {example['question']}\n"
            prompt += f"A: {example['answer']}\n"
        
        prompt += "\n" + "="*50 + "\n\n"
        
        # Add context if provided
        if context_data:
            prompt += f"Context Information:\n{context_data}\n\n"
        
        # Add relevant products if provided
        if relevant_products:
            prompt += "Relevant Product Data:\n"
            for i, product in enumerate(relevant_products[:10], 1):  # Limit to 10 products
                prompt += f"{i}. {product}\n"
            prompt += "\n"
        
        # Add the actual question
        prompt += f"User Question: {user_question}\n\n"
        prompt += "Please provide a helpful, accurate answer based on the context and data provided. "
        prompt += "If you need to reference specific products or prices, include them in your response."
        
        return prompt
    
    @staticmethod
    def build_summary_prompt(data_summary: Dict) -> str:
        """
        Build a prompt for generating dataset summary.
        
        Args:
            data_summary: Dictionary containing summary statistics
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""{PromptEngine.SYSTEM_PROMPT}

Please analyze the following dataset summary and provide a comprehensive business report:

Dataset Statistics:
- Total Products: {data_summary.get('total_products', 'N/A')}
- Total Unique SKUs: {data_summary.get('total_skus', 'N/A')}
- Total Unique Styles: {data_summary.get('total_styles', 'N/A')}

Category Distribution:
{_format_dict(data_summary.get('categories', {}))}

Catalog Distribution:
{_format_dict(data_summary.get('catalogs', {}))}

Price Statistics:
- Minimum Price: ₹{data_summary.get('price_statistics', {}).get('min_price_overall', 'N/A')}
- Maximum Price: ₹{data_summary.get('price_statistics', {}).get('max_price_overall', 'N/A')}
- Average Price: ₹{data_summary.get('price_statistics', {}).get('avg_price_overall', 'N/A'):.2f}
- Median Price: ₹{data_summary.get('price_statistics', {}).get('median_price_overall', 'N/A'):.2f}

Platform Analysis:
{_format_platform_analysis(data_summary.get('platform_analysis', {}))}

Please provide:
1. Executive Summary (2-3 sentences)
2. Key Insights (bullet points)
3. Product Diversity Analysis
4. Pricing Trends and Patterns
5. Platform Comparison Highlights
6. Recommendations for Business Decision-Making

Format the response in a clear, professional manner suitable for business stakeholders.
"""
        return prompt
    
    @staticmethod
    def build_price_comparison_prompt(
        product_category: Optional[str] = None,
        style_id: Optional[str] = None,
        platform_comparison: Dict[str, float] = None
    ) -> str:
        """
        Build a prompt for price comparison analysis.
        
        Args:
            product_category: Optional category filter
            style_id: Optional style ID filter
            platform_comparison: Dictionary of platform -> average price
            
        Returns:
            Formatted prompt string
        """
        prompt = f"{PromptEngine.SYSTEM_PROMPT}\n\n"
        
        if product_category:
            prompt += f"Analyzing price comparison for category: {product_category}\n\n"
        
        if style_id:
            prompt += f"Analyzing price comparison for style: {style_id}\n\n"
        
        if platform_comparison:
            prompt += "Platform Price Comparison:\n"
            for platform, avg_price in sorted(platform_comparison.items(), key=lambda x: x[1]):
                prompt += f"- {platform.capitalize()}: ₹{avg_price:.2f}\n"
            prompt += "\n"
        
        prompt += "Please provide:\n"
        prompt += "1. Which platform offers the best prices overall\n"
        prompt += "2. Price differences and potential savings\n"
        prompt += "3. Recommendations for cost-conscious shoppers\n"
        prompt += "4. Any notable patterns or insights"
        
        return prompt


def _format_dict(d: Dict) -> str:
    """Helper function to format dictionary for prompts."""
    if not d:
        return "N/A"
    return "\n".join([f"- {k}: {v}" for k, v in d.items()])


def _format_platform_analysis(platform_analysis: Dict) -> str:
    """Helper function to format platform analysis for prompts."""
    if not platform_analysis:
        return "N/A"
    
    formatted = []
    for platform, stats in platform_analysis.items():
        formatted.append(f"\n{platform.capitalize()}:")
        formatted.append(f"  - Products Available: {stats.get('products_available', 'N/A')}")
        formatted.append(f"  - Price Range: ₹{stats.get('min_price', 'N/A')} - ₹{stats.get('max_price', 'N/A')}")
        formatted.append(f"  - Average Price: ₹{stats.get('avg_price', 'N/A'):.2f}")
    
    return "\n".join(formatted)

