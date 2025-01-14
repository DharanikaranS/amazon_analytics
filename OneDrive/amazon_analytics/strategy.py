from abc import ABC, abstractmethod

class ProductStrategy(ABC):
    @abstractmethod
    def product_finder(self):
        pass
    
    @abstractmethod
    def brand_performance(self):
        pass

    @abstractmethod
    def discount_analytics(self):
        pass

    @abstractmethod
    def price_history(self):
        pass

    @abstractmethod
    def feedback(self):
        pass

class MobilePhoneStrategy(ProductStrategy):
    def product_finder(self):
        return "Mobile phone finder data"

    def brand_performance(self):
        return "Mobile phone brand performance data"
    
    def discount_analytics(self):
        return "Mobile phone discount analytics"

    def price_history(self):
        return "Mobile phone price history"

    def feedback(self):
        return "Mobile phone feedback data"

class LaptopStrategy(ProductStrategy):
    def product_finder(self):
        return "Laptop finder data"
    
    def brand_performance(self):
        return "Laptop brand performance data"
    
    def discount_analytics(self):
        return "Laptop discount analytics"

    def price_history(self):
        return "Laptop price history"

    def feedback(self):
        return "Laptop feedback data"

class CameraStrategy(ProductStrategy):
    def product_finder(self):
        return "Camera finder data"
    
    def brand_performance(self):
        return "Camera brand performance data"
    
    def discount_analytics(self):
        return "Camera discount analytics"

    def price_history(self):
        return "Camera price history"

    def feedback(self):
        return "Camera feedback data"

class TShirtStrategy(ProductStrategy):
    def product_finder(self):
        return "T-shirt finder data"
    
    def brand_performance(self):
        return "T-shirt brand performance data"
    
    def discount_analytics(self):
        return "T-shirt discount analytics"

    def price_history(self):
        return "T-shirt price history"

    def feedback(self):
        return "T-shirt feedback data"

class SneakerStrategy(ProductStrategy):
    def product_finder(self):
        return "Sneaker finder data"
    
    def brand_performance(self):
        return "Sneaker brand performance data"
    
    def discount_analytics(self):
        return "Sneaker discount analytics"

    def price_history(self):
        return "Sneaker price history"

    def feedback(self):
        return "Sneaker feedback data"
