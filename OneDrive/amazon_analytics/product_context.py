# product_context.py

from strategy import ProductStrategy

class ProductContext:
    def __init__(self, strategy: ProductStrategy):
        self._strategy = strategy  # Assigns a specific product strategy

    def get_data(self):
        # Uses the methods defined in the strategy to gather all product-specific data
        return {
            "product_finder": self._strategy.product_finder(),
            "brand_performance": self._strategy.brand_performance(),
            "discount_analytics": self._strategy.discount_analytics(),
            "price_history": self._strategy.price_history(),
            "feedback": self._strategy.feedback()
        }
