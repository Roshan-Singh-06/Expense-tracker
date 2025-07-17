"""
AI-Powered Expense Categorization Module
Uses machine learning to automatically categorize expenses
"""

import re
import pickle
import os
from datetime import datetime
import json

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class AIExpenseCategorizer:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_file = "ai_categorizer_model.pkl"
        self.categories = [
            "🍕 Food", "🚗 Transportation", "🛒 Shopping",
            "🎬 Entertainment", "💊 Healthcare", "🏠 Bills",
            "🎓 Education", "💼 Business", "🎁 Gifts", "🏋️ Fitness"
        ]
        
        # Load pre-trained model if available
        self.load_model()
        
        # Rule-based fallback system with improved keywords
        self.category_keywords = {
            "Food": [
                # Restaurants and food places
                "restaurant", "food", "dinner", "lunch", "breakfast", "cafe", "coffee",
                "pizza", "burger", "sandwich", "meal", "eat", "dining", "kitchen",
                "grocery", "supermarket", "vegetables", "fruits", "snacks", "drink",
                "bar", "pub", "takeaway", "delivery", "swiggy", "zomato", "dominos",
                "mcdonalds", "kfc", "subway", "starbucks", "chai", "tea", "juice",
                "bakery", "ice cream", "sweet", "milk", "bread", "rice", "dal",
                "chicken", "mutton", "fish", "biryani", "dosa", "idli", "vada",
                # Grocery items
                "groceries", "market", "vegetables", "fruits", "cooking", "spices"
            ],
            "Transportation": [
                # Ride services
                "uber", "ola", "taxi", "auto", "rickshaw", "cab", "ride",
                # Public transport
                "bus", "metro", "train", "flight", "airplane", "railway",
                # Vehicle expenses
                "fuel", "petrol", "diesel", "gas", "parking", "toll", "challan",
                # Travel
                "ticket", "travel", "transport", "bike", "car", "vehicle",
                "booking", "irctc", "goibibo", "makemytrip"
            ],
            "Shopping": [
                # Online shopping
                "amazon", "flipkart", "myntra", "ajio", "nykaa", "shop", "shopping",
                # Physical stores
                "store", "mall", "market", "buy", "purchase", "sale",
                # Items
                "clothes", "shoes", "dress", "shirt", "pants", "bag", "watch",
                "electronics", "mobile", "phone", "laptop", "gadget", "appliance",
                "furniture", "home", "decoration", "gift"
            ],
            "Entertainment": [
                # Streaming and digital
                "netflix", "amazon prime", "hotstar", "spotify", "youtube", "music",
                "subscription", "app", "game", "gaming",
                # Events and venues
                "movie", "cinema", "theatre", "concert", "show", "party", "club",
                "fun", "entertainment", "festival", "event", "ticket", "bookmyshow"
            ],
            "Healthcare": [
                # Medical services
                "doctor", "hospital", "clinic", "medical", "health", "dental", "dentist",
                "checkup", "treatment", "surgery", "consultation", "appointment",
                # Medicines and supplies
                "medicine", "pharmacy", "drug", "tablet", "prescription", "vitamin",
                "supplement", "lab", "test", "xray", "scan", "insurance"
            ],
            "Bills": [
                # Utilities
                "electricity", "water", "gas", "utility", "bill", "payment",
                # Internet and communication
                "internet", "wifi", "broadband", "phone", "mobile", "recharge",
                "airtel", "jio", "vodafone", "bsnl",
                # Housing
                "rent", "maintenance", "society", "apartment", "house",
                # Other bills
                "cable", "tv", "insurance", "loan", "emi", "bank", "credit card"
            ],
            "Education": [
                "school", "college", "university", "course", "book", "study",
                "education", "tuition", "fee", "exam", "certification", "training",
                "workshop", "seminar", "library", "stationery", "notebook",
                "online course", "udemy", "coursera", "skill"
            ],
            "Other": [
                "miscellaneous", "other", "unknown", "cash", "atm", "withdrawal",
                "transfer", "salary", "income", "refund", "return"
            ]
        }
    
    def smart_categorize(self, description, amount=0):
        """
        Enhanced AI-powered smart categorization with multiple methods
        Returns (category, confidence_score)
        """
        description_clean = self._clean_description(description)
        
        if not description_clean:
            return "Other", 0.1
        
        # Method 1: Enhanced rule-based keyword matching
        rule_category, rule_confidence = self._categorize_by_enhanced_rules(description_clean)
        if rule_confidence > 0.7:
            return rule_category, rule_confidence
        
        # Method 2: Pattern matching for common phrases
        pattern_category, pattern_confidence = self._categorize_by_patterns(description_clean)
        if pattern_confidence > 0.8:
            return pattern_category, pattern_confidence
        
        # Method 3: Amount-based heuristics
        amount_category = self._categorize_by_amount(description_clean, amount)
        if amount_category and rule_confidence < 0.5:
            return amount_category, 0.6
        
        # Return best match
        if rule_confidence > 0.3:
            return rule_category, rule_confidence
        elif pattern_confidence > 0.3:
            return pattern_category, pattern_confidence
        else:
            return "Other", 0.2
    
    def _categorize_by_enhanced_rules(self, description):
        """Enhanced categorization using improved keyword matching"""
        max_score = 0
        best_category = "Other"
        
        words = set(description.split())  # Use set for faster lookup
        
        for category, keywords in self.category_keywords.items():
            score = 0
            matched_keywords = 0
            total_keyword_chars = 0
            matched_chars = 0
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Exact phrase match in description
                if keyword_lower in description:
                    score += 2.0  # Higher weight for exact matches
                    matched_keywords += 1
                    matched_chars += len(keyword_lower)
                    total_keyword_chars += len(keyword_lower)
                    continue
                
                # Individual word matches
                keyword_words = keyword_lower.split()
                if len(keyword_words) == 1:
                    if keyword_lower in words:
                        score += 1.5
                        matched_keywords += 1
                        matched_chars += len(keyword_lower)
                else:
                    # Multi-word keyword - check if all words present
                    if all(word in words for word in keyword_words):
                        score += 2.5  # High score for multi-word matches
                        matched_keywords += 1
                        matched_chars += len(keyword_lower)
                
                total_keyword_chars += len(keyword_lower)
            
            # Calculate confidence based on matches
            if len(keywords) > 0 and total_keyword_chars > 0:
                # Base score normalized by keyword count
                base_score = score / len(keywords)
                
                # Character coverage bonus
                char_coverage = matched_chars / total_keyword_chars if total_keyword_chars > 0 else 0
                
                # Multiple match bonus
                match_bonus = min(matched_keywords / len(keywords), 1.0)
                
                # Combined confidence score
                final_score = (base_score * 0.5) + (char_coverage * 0.3) + (match_bonus * 0.2)
                
                if final_score > max_score:
                    max_score = final_score
                    best_category = category
        
        return best_category, min(max_score, 1.0)
    
    def _categorize_by_patterns(self, description):
        """Categorize using common spending patterns"""
        patterns = {
            "Food": [
                r'\b(bought|ordered|ate|had)\s+(food|dinner|lunch|breakfast)',
                r'\b(restaurant|cafe|hotel|dhaba)\b',
                r'\b(zomato|swiggy|dominos|pizza|burger)\b',
                r'\b(grocery|vegetables|fruits|milk|bread)\b'
            ],
            "Transportation": [
                r'\b(uber|ola|taxi|auto|cab)\s+(ride|trip|booking)',
                r'\b(bus|train|metro|flight)\s+(ticket|fare)',
                r'\b(fuel|petrol|diesel)\s+(filled|tank)',
                r'\b(parking|toll|challan)\b'
            ],
            "Shopping": [
                r'\b(amazon|flipkart|myntra)\b',
                r'\b(bought|purchased|ordered)\s+(clothes|shoes|mobile|laptop)',
                r'\b(shopping|mall|store)\b'
            ],
            "Entertainment": [
                r'\b(movie|cinema|show|concert)\s+(ticket|booking)',
                r'\b(netflix|spotify|prime)\s+(subscription|payment)',
                r'\b(game|gaming|entertainment)\b'
            ],
            "Healthcare": [
                r'\b(doctor|hospital|clinic)\s+(visit|consultation|checkup)',
                r'\b(medicine|pharmacy|drug|tablet)\b',
                r'\b(medical|health|dental)\s+(bill|payment|insurance)'
            ],
            "Bills": [
                r'\b(electricity|water|gas|internet|wifi)\s+(bill|payment)',
                r'\b(mobile|phone)\s+(recharge|bill)',
                r'\b(rent|maintenance|emi)\s+(payment|paid)'
            ]
        }
        
        max_confidence = 0
        best_category = "Other"
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, description, re.IGNORECASE):
                    confidence = 0.8 + (0.2 * len(re.findall(pattern, description, re.IGNORECASE)))
                    if confidence > max_confidence:
                        max_confidence = min(confidence, 1.0)
                        best_category = category
        
        return best_category, max_confidence
    
    def _clean_description(self, description):
        """Clean and normalize the description"""
        if not description:
            return ""
        
        # Convert to lowercase
        desc = description.lower().strip()
        
        # Remove special characters but keep spaces
        desc = re.sub(r'[^\w\s]', ' ', desc)
        
        # Remove extra whitespaces
        desc = re.sub(r'\s+', ' ', desc)
        
        return desc
    
    def _predict_with_ml(self, description):
        """Predict category using trained ML model"""
        if not self.model or not self.vectorizer:
            return None, 0
        
        try:
            # Transform description
            X = self.vectorizer.transform([description])
            
            # Predict
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            confidence = max(probabilities)
            
            return prediction, confidence
        except Exception:
            return None, 0
    
    def _categorize_by_rules(self, description):
        """Categorize using keyword rules"""
        max_score = 0
        best_category = "🛒 Shopping"
        
        words = description.split()
        
        for category, keywords in self.category_keywords.items():
            score = 0
            matched_keywords = 0
            
            for keyword in keywords:
                if keyword in description:
                    # Exact phrase match gets higher score
                    score += 1.0
                    matched_keywords += 1
                else:
                    # Check for partial matches
                    for word in words:
                        if keyword in word or word in keyword:
                            score += 0.5
                            matched_keywords += 1
                            break
            
            # Normalize score by number of keywords
            if len(keywords) > 0:
                normalized_score = score / len(keywords)
                
                # Boost score if multiple keywords matched
                if matched_keywords > 1:
                    normalized_score *= 1.2
                
                if normalized_score > max_score:
                    max_score = normalized_score
                    best_category = category
        
        return best_category, min(max_score, 1.0)
    
    def _categorize_by_amount(self, description, amount):
        """Enhanced amount-based heuristics for categorization"""
        if amount <= 0:
            return None
        
        # Very small amounts (< ₹100) - likely food, transport, or small purchases
        if amount < 100:
            if any(word in description for word in ["coffee", "tea", "snack", "chai", "juice", "water"]):
                return "Food"
            elif any(word in description for word in ["auto", "bus", "metro", "parking", "toll"]):
                return "Transportation"
            return "Food"  # Most small amounts are food-related
        
        # Small amounts (₹100-500) - food, transport, entertainment
        elif 100 <= amount < 500:
            if any(word in description for word in ["movie", "game", "ticket", "entertainment"]):
                return "Entertainment"
            elif any(word in description for word in ["uber", "ola", "taxi", "fuel", "petrol"]):
                return "Transportation"
            elif any(word in description for word in ["medicine", "pharmacy", "doctor"]):
                return "Healthcare"
            return None  # Let keyword matching handle this range
        
        # Medium amounts (₹500-2000) - shopping, bills, dining
        elif 500 <= amount < 2000:
            if any(word in description for word in ["restaurant", "hotel", "dining", "dinner"]):
                return "Food"
            elif any(word in description for word in ["clothes", "shoes", "shopping", "mall"]):
                return "Shopping"
            elif any(word in description for word in ["bill", "recharge", "internet", "mobile"]):
                return "Bills"
            return None
        
        # Large amounts (₹2000-10000) - major shopping, bills, healthcare
        elif 2000 <= amount < 10000:
            if any(word in description for word in ["rent", "maintenance", "electricity", "insurance"]):
                return "Bills"
            elif any(word in description for word in ["laptop", "phone", "tv", "electronics", "appliance"]):
                return "Shopping"
            elif any(word in description for word in ["hospital", "surgery", "treatment", "medical"]):
                return "Healthcare"
            return "Shopping"  # Most large amounts are shopping
        
        # Very large amounts (> ₹10000) - major bills, purchases, investments
        else:
            if any(word in description for word in ["rent", "emi", "loan", "insurance"]):
                return "Bills"
            elif any(word in description for word in ["laptop", "mobile", "car", "bike", "gold", "investment"]):
                return "Shopping"
            return "Bills"  # Most very large amounts are bills/EMIs
        
        return None
    
    def train_on_user_data(self, expenses):
        """Train the model on user's historical data"""
        if not SKLEARN_AVAILABLE or len(expenses) < 10:
            return False
        
        try:
            # Prepare training data
            descriptions = []
            categories = []
            
            for expense in expenses:
                if expense.get('description') and expense.get('category'):
                    desc_clean = self._clean_description(expense['description'])
                    if desc_clean:  # Only add non-empty descriptions
                        descriptions.append(desc_clean)
                        categories.append(expense['category'])
            
            if len(descriptions) < 5:  # Need minimum data
                return False
            
            # Create and train model
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
            X = self.vectorizer.fit_transform(descriptions)
            
            self.model = MultinomialNB(alpha=0.1)
            self.model.fit(X, categories)
            
            # Save the trained model
            self.save_model()
            
            return True
        except Exception as e:
            print(f"Training error: {e}")
            return False
    
    def save_model(self):
        """Save the trained model to disk"""
        if self.model and self.vectorizer:
            try:
                model_data = {
                    'model': self.model,
                    'vectorizer': self.vectorizer,
                    'categories': self.categories,
                    'trained_date': datetime.now().isoformat()
                }
                
                with open(self.model_file, 'wb') as f:
                    pickle.dump(model_data, f)
                
                return True
            except Exception as e:
                print(f"Model save error: {e}")
                return False
        return False
    
    def load_model(self):
        """Load pre-trained model from disk"""
        if os.path.exists(self.model_file):
            try:
                with open(self.model_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.model = model_data.get('model')
                self.vectorizer = model_data.get('vectorizer')
                self.categories = model_data.get('categories', self.categories)
                
                return True
            except Exception as e:
                print(f"Model load error: {e}")
                return False
        return False
    
    def get_category_suggestions(self, description, top_n=3):
        """Get top N category suggestions for a description"""
        suggestions = []
        
        # Get all categories with their confidence scores
        for category in self.categories:
            # Temporarily modify description to check each category
            test_desc = f"{description} {category.lower()}"
            _, confidence = self.smart_categorize(test_desc)
            suggestions.append((category, confidence))
        
        # Sort by confidence and return top N
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:top_n]
    
    def update_model_with_feedback(self, description, actual_category, predicted_category):
        """Update model with user feedback (for continuous learning)"""
        feedback_file = "categorizer_feedback.json"
        
        feedback_entry = {
            'description': description,
            'predicted': predicted_category,
            'actual': actual_category,
            'timestamp': datetime.now().isoformat()
        }
        
        # Load existing feedback
        feedback_data = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r') as f:
                    feedback_data = json.load(f)
            except:
                feedback_data = []
        
        # Add new feedback
        feedback_data.append(feedback_entry)
        
        # Save updated feedback
        try:
            with open(feedback_file, 'w') as f:
                json.dump(feedback_data, f, indent=2)
        except Exception as e:
            print(f"Feedback save error: {e}")
        
        # Retrain if we have enough feedback data
        if len(feedback_data) >= 20:
            self._retrain_with_feedback(feedback_data)
    
    def _retrain_with_feedback(self, feedback_data):
        """Retrain model with user feedback data"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            descriptions = [item['description'] for item in feedback_data]
            categories = [item['actual'] for item in feedback_data]
            
            # Clean descriptions
            clean_descriptions = [self._clean_description(desc) for desc in descriptions]
            
            # Retrain
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
            X = self.vectorizer.fit_transform(clean_descriptions)
            
            self.model = MultinomialNB(alpha=0.1)
            self.model.fit(X, categories)
            
            # Save updated model
            self.save_model()
            
            print("Model retrained with user feedback!")
        except Exception as e:
            print(f"Retraining error: {e}")


# Test function
def test_categorizer():
    """Test the AI categorizer"""
    categorizer = AIExpenseCategorizer()
    
    test_cases = [
        ("Lunch at McDonald's", 250),
        ("Uber ride to office", 150),
        ("Netflix subscription", 199),
        ("Grocery shopping at Big Bazaar", 1500),
        ("Doctor consultation", 500),
        ("Electricity bill payment", 2000),
        ("Gym membership", 3000),
        ("Birthday gift for friend", 800)
    ]
    
    print("AI Categorizer Test Results:")
    print("=" * 50)
    
    for description, amount in test_cases:
        category, confidence = categorizer.smart_categorize(description, amount)
        print(f"Description: {description}")
        print(f"Amount: ₹{amount}")
        print(f"Predicted Category: {category}")
        print(f"Confidence: {confidence:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    test_categorizer()
