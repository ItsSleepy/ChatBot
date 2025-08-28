import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import random
import json
import datetime
from collections import defaultdict
import threading
import webbrowser
import os

# Try to import NLTK for advanced features
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('sentiment/vader_lexicon')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available. Using basic text processing.")

class AdvancedChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Advanced AI ChatBot Studio")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0d1117')
        
        # Colors
        self.colors = {
            'bg_dark': '#0d1117',
            'bg_medium': '#161b22',
            'bg_light': '#21262d',
            'accent': '#58a6ff',
            'accent_hover': '#1f6feb',
            'text_primary': '#f0f6fc',
            'text_secondary': '#8b949e',
            'user_bubble': '#238636',
            'bot_bubble': '#1f6feb',
            'success': '#56d364',
            'warning': '#e3b341',
            'error': '#f85149'
        }
        
        # Chat state
        self.conversation_history = []
        self.user_profile = {
            'name': None,
            'preferences': {},
            'mood_history': [],
            'topics_discussed': defaultdict(int)
        }
        
        # Bot personality settings
        self.bot_settings = {
            'personality': 'friendly',  # friendly, professional, humorous, technical
            'response_style': 'detailed',  # brief, detailed, creative
            'learning_mode': True,
            'mood_detection': True
        }
        
        # Initialize NLTK components if available
        if NLTK_AVAILABLE:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        
        self.setup_knowledge_base()
        self.setup_gui()
        self.greet_user()
        
    def setup_knowledge_base(self):
        """Initialize the bot's knowledge base"""
        self.knowledge_base = {
            # Greetings and basic interactions
            'greetings': {
                'patterns': [r'\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b'],
                'responses': [
                    "Hello! 👋 I'm your AI assistant. How can I help you today?",
                    "Hi there! 😊 What would you like to chat about?",
                    "Greetings! I'm here to help. What's on your mind?",
                    "Hey! 🤖 Ready for an interesting conversation?"
                ]
            },
            
            # Farewells
            'farewells': {
                'patterns': [r'\b(bye|goodbye|see you|farewell|take care|exit|quit)\b'],
                'responses': [
                    "Goodbye! 👋 It was great chatting with you!",
                    "See you later! 😊 Have a wonderful day!",
                    "Take care! Feel free to come back anytime.",
                    "Farewell! 🤖 Hope our conversation was helpful!"
                ]
            },
            
            # Questions about the bot
            'bot_info': {
                'patterns': [r'\b(who are you|what are you|your name|about you|tell me about yourself)\b'],
                'responses': [
                    "I'm an advanced AI chatbot! 🤖 I can help with questions, have conversations, and even detect your mood!",
                    "I'm your friendly AI assistant, designed to chat, help, and learn from our conversations!",
                    "I'm an intelligent chatbot with personality! I can discuss various topics and adapt to your communication style."
                ]
            },
            
            # How are you
            'how_are_you': {
                'patterns': [r'\b(how are you|how do you feel|what\'s up|how\'s it going)\b'],
                'responses': [
                    "I'm doing great! 😊 My circuits are buzzing with excitement to chat with you!",
                    "I'm fantastic! 🌟 Every conversation energizes my algorithms!",
                    "I'm wonderful! Ready to tackle any topic you throw at me! 💪"
                ]
            },
            
            # Technology topics
            'technology': {
                'patterns': [r'\b(programming|coding|python|javascript|ai|artificial intelligence|machine learning|computer|software|hardware|tech)\b'],
                'responses': [
                    "Technology is fascinating! 💻 I love discussing programming, AI, and the latest tech trends. What specific area interests you?",
                    "Oh, a fellow tech enthusiast! 🚀 From Python to AI, there's so much to explore. What would you like to know?",
                    "Technology is evolving so rapidly! Whether it's coding, AI, or hardware, I'm here to discuss it all! 🔧"
                ]
            },
            
            # Weather
            'weather': {
                'patterns': [r'\b(weather|rain|sunny|cloudy|temperature|forecast|climate)\b'],
                'responses': [
                    "I wish I could check the weather for you! 🌤️ Try asking a weather service or checking your local forecast.",
                    "Weather affects our mood so much! ☀️🌧️ How's the weather treating you today?",
                    "I can't access real-time weather data, but I'd love to chat about how weather impacts our daily lives! 🌈"
                ]
            },
            
            # Hobbies and interests
            'hobbies': {
                'patterns': [r'\b(hobby|hobbies|interests|music|movies|books|reading|gaming|sports|art|cooking)\b'],
                'responses': [
                    "Hobbies make life so much richer! 🎨 I'd love to hear about your interests. What do you enjoy doing in your free time?",
                    "That sounds interesting! 🎯 Hobbies are a great way to express creativity and relax. Tell me more!",
                    "I find human hobbies fascinating! 🎪 From music to sports to art - there's so much diversity in what people enjoy!"
                ]
            },
            
            # Emotions and mood
            'emotions': {
                'patterns': [r'\b(sad|happy|angry|frustrated|excited|worried|anxious|depressed|joyful|stressed)\b'],
                'responses': [
                    "I understand emotions can be complex. 💙 Would you like to talk about what's affecting your mood?",
                    "Feelings are important and valid. 🤗 I'm here to listen if you want to share what's on your mind.",
                    "Emotions are part of what makes us human (and interesting to an AI like me!). How are you feeling right now?"
                ]
            },
            
            # Help and assistance
            'help': {
                'patterns': [r'\b(help|assist|support|confused|don\'t know|stuck|problem)\b'],
                'responses': [
                    "I'm here to help! 🆘 What specific problem or question can I assist you with?",
                    "No worries! 🤝 Everyone needs help sometimes. Tell me what's troubling you and let's work through it together.",
                    "That's what I'm here for! 💡 Describe your issue and I'll do my best to provide useful guidance."
                ]
            },
            
            # Learning and education
            'learning': {
                'patterns': [r'\b(learn|study|education|school|university|course|tutorial|knowledge|teach)\b'],
                'responses': [
                    "Learning is amazing! 📚 I love helping people discover new knowledge. What subject interests you?",
                    "Education opens so many doors! 🎓 Whether it's formal study or self-learning, I'm here to support your journey.",
                    "Knowledge is power! 💪 I can help explain concepts, suggest resources, or just discuss learning strategies."
                ]
            },
            
            # Default responses for unmatched input
            'default': [
                "That's interesting! 🤔 Can you tell me more about that?",
                "I'm not sure I fully understand, but I'd love to learn more! 💭",
                "Hmm, that's a new one for me! 🧠 Could you elaborate?",
                "I find that topic intriguing! 🌟 What's your perspective on it?",
                "Tell me more! 📖 I'm always eager to learn from our conversations."
            ]
        }
        
        # Advanced conversation topics
        self.advanced_topics = {
            'philosophy': [
                "Philosophy makes me think about consciousness and existence! 🤔 What philosophical questions fascinate you?",
                "The big questions of life! 💭 From ethics to metaphysics, philosophy explores the deepest aspects of reality.",
                "I love philosophical discussions! 🧠 They challenge us to think beyond the obvious."
            ],
            'science': [
                "Science is the quest to understand our universe! 🔬 From quantum physics to biology, what area captivates you?",
                "The scientific method has given us incredible insights! 🌌 What scientific discoveries amaze you most?",
                "Science fiction often becomes science fact! 🚀 I'm fascinated by how human curiosity drives discovery."
            ],
            'creativity': [
                "Creativity is one of humanity's greatest gifts! 🎨 How do you express your creative side?",
                "Art, music, writing - creativity takes so many forms! 🌈 What inspires your imagination?",
                "I'm amazed by human creativity! 💫 Even as an AI, I try to be creative in my responses."
            ]
        }
    
    def setup_gui(self):
        """Setup the graphical user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg=self.colors['bg_dark'], height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🤖 Advanced AI ChatBot Studio",
                              bg=self.colors['bg_dark'], 
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 18, 'bold'))
        title_label.pack(pady=20)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Paned window for chat and settings
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, 
                              bg=self.colors['bg_dark'], sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Chat panel
        chat_panel = tk.Frame(paned, bg=self.colors['bg_medium'])
        # Settings panel
        settings_panel = tk.Frame(paned, bg=self.colors['bg_medium'], width=300)
        
        paned.add(chat_panel, minsize=600)
        paned.add(settings_panel, minsize=250)
        
        self.setup_chat_panel(chat_panel)
        self.setup_settings_panel(settings_panel)
        
        # Status bar
        self.setup_status_bar()
    
    def setup_chat_panel(self, parent):
        """Setup the main chat interface"""
        # Chat display area
        chat_frame = tk.Frame(parent, bg=self.colors['bg_medium'])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat history
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11),
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=25
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure text tags for styling
        self.chat_display.tag_config('user', foreground=self.colors['user_bubble'], font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config('bot', foreground=self.colors['bot_bubble'], font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_config('timestamp', foreground=self.colors['text_secondary'], font=('Segoe UI', 9))
        self.chat_display.tag_config('mood', foreground=self.colors['warning'], font=('Segoe UI', 9, 'italic'))
        
        # Input area
        input_frame = tk.Frame(chat_frame, bg=self.colors['bg_medium'])
        input_frame.pack(fill=tk.X)
        
        # Input field
        self.user_input = tk.Text(input_frame, 
                                 bg=self.colors['bg_light'], 
                                 fg=self.colors['text_primary'],
                                 font=('Segoe UI', 11),
                                 height=3,
                                 wrap=tk.WORD)
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Send button
        send_btn = tk.Button(input_frame,
                           text="📤\nSend",
                           command=self.send_message,
                           bg=self.colors['accent'],
                           fg='white',
                           font=('Segoe UI', 10, 'bold'),
                           width=8,
                           height=2)
        send_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.user_input.bind('<Return>', self.on_enter)
        self.user_input.bind('<Shift-Return>', self.on_shift_enter)
        
        # Quick action buttons
        quick_frame = tk.Frame(chat_frame, bg=self.colors['bg_medium'])
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        quick_buttons = [
            ("❓ Ask Question", lambda: self.insert_template("I have a question about ")),
            ("💡 Get Help", lambda: self.insert_template("Can you help me with ")),
            ("🎯 Topic", lambda: self.insert_template("Let's talk about ")),
            ("🔄 Clear Chat", self.clear_chat)
        ]
        
        for text, command in quick_buttons:
            btn = tk.Button(quick_frame, text=text, command=command,
                          bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                          font=('Segoe UI', 9), relief=tk.FLAT, padx=10)
            btn.pack(side=tk.LEFT, padx=5)
    
    def setup_settings_panel(self, parent):
        """Setup the bot settings and info panel"""
        # Settings header
        settings_label = tk.Label(parent, text="🛠️ Bot Settings", 
                                bg=self.colors['bg_medium'], fg=self.colors['text_primary'],
                                font=('Segoe UI', 14, 'bold'))
        settings_label.pack(pady=10)
        
        # Notebook for different setting categories
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Personality tab
        personality_frame = tk.Frame(notebook, bg=self.colors['bg_light'])
        notebook.add(personality_frame, text=" 🎭 Personality ")
        
        # Stats tab
        stats_frame = tk.Frame(notebook, bg=self.colors['bg_light'])
        notebook.add(stats_frame, text=" 📊 Statistics ")
        
        # Features tab
        features_frame = tk.Frame(notebook, bg=self.colors['bg_light'])
        notebook.add(features_frame, text=" ⚡ Features ")
        
        self.setup_personality_settings(personality_frame)
        self.setup_statistics_panel(stats_frame)
        self.setup_features_panel(features_frame)
    
    def setup_personality_settings(self, parent):
        """Setup personality configuration"""
        # Personality selection
        personality_label = tk.Label(parent, text="Bot Personality:",
                                   bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                   font=('Segoe UI', 10, 'bold'))
        personality_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.personality_var = tk.StringVar(value=self.bot_settings['personality'])
        personalities = ["friendly", "professional", "humorous", "technical"]
        
        for personality in personalities:
            rb = tk.Radiobutton(parent, text=personality.title(), 
                              variable=self.personality_var, value=personality,
                              bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                              font=('Segoe UI', 9), selectcolor=self.colors['bg_dark'],
                              command=self.update_personality)
            rb.pack(anchor=tk.W, padx=20)
        
        # Response style
        tk.Label(parent, text="Response Style:",
                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(20, 5))
        
        self.style_var = tk.StringVar(value=self.bot_settings['response_style'])
        styles = ["brief", "detailed", "creative"]
        
        for style in styles:
            rb = tk.Radiobutton(parent, text=style.title(),
                              variable=self.style_var, value=style,
                              bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                              font=('Segoe UI', 9), selectcolor=self.colors['bg_dark'],
                              command=self.update_style)
            rb.pack(anchor=tk.W, padx=20)
        
        # Learning mode toggle
        self.learning_var = tk.BooleanVar(value=self.bot_settings['learning_mode'])
        learning_cb = tk.Checkbutton(parent, text="Learning Mode",
                                   variable=self.learning_var,
                                   bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                   font=('Segoe UI', 10), selectcolor=self.colors['bg_dark'],
                                   command=self.toggle_learning)
        learning_cb.pack(anchor=tk.W, padx=10, pady=(20, 5))
        
        # Mood detection toggle
        self.mood_var = tk.BooleanVar(value=self.bot_settings['mood_detection'])
        mood_cb = tk.Checkbutton(parent, text="Mood Detection",
                               variable=self.mood_var,
                               bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                               font=('Segoe UI', 10), selectcolor=self.colors['bg_dark'],
                               command=self.toggle_mood_detection)
        mood_cb.pack(anchor=tk.W, padx=10, pady=5)
    
    def setup_statistics_panel(self, parent):
        """Setup statistics display"""
        self.stats_text = scrolledtext.ScrolledText(
            parent,
            bg=self.colors['bg_dark'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 9),
            height=15,
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Update button
        update_btn = tk.Button(parent, text="🔄 Update Stats",
                             command=self.update_statistics,
                             bg=self.colors['accent'], fg='white',
                             font=('Segoe UI', 9))
        update_btn.pack(pady=10)
    
    def setup_features_panel(self, parent):
        """Setup features information"""
        features_text = """🌟 Advanced Features:

🤖 Intelligent Responses
• Pattern-based understanding
• Context-aware replies
• Personality adaptation

💭 Mood Detection
• Sentiment analysis
• Emotional awareness
• Empathetic responses

🧠 Learning Capabilities
• Conversation memory
• Preference tracking
• Topic analysis

🎯 Smart Features
• Quick templates
• Rich text formatting
• Conversation export

📊 Analytics
• Usage statistics
• Mood tracking
• Topic insights"""
        
        features_label = tk.Label(parent, text=features_text,
                                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                font=('Segoe UI', 9), justify=tk.LEFT)
        features_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Export conversation button
        export_btn = tk.Button(parent, text="📄 Export Chat",
                             command=self.export_conversation,
                             bg=self.colors['success'], fg='white',
                             font=('Segoe UI', 9))
        export_btn.pack(pady=10)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_frame = tk.Frame(self.root, bg=self.colors['bg_medium'], height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="🟢 ChatBot Ready",
                                   bg=self.colors['bg_medium'], fg=self.colors['success'],
                                   font=('Segoe UI', 10))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Message counter
        self.message_count_label = tk.Label(self.status_frame, text="Messages: 0",
                                          bg=self.colors['bg_medium'], fg=self.colors['text_secondary'],
                                          font=('Segoe UI', 10))
        self.message_count_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def greet_user(self):
        """Initial greeting"""
        greeting = "🤖 Hello! I'm your Advanced AI ChatBot! I'm here to chat, help, and learn from our conversation. What would you like to talk about today?"
        self.add_message("ChatBot", greeting, "bot")
        
        if NLTK_AVAILABLE:
            self.add_message("System", "🧠 Advanced NLP features enabled - I can detect mood and understand context better!", "mood")
        else:
            self.add_message("System", "💭 Running in basic mode - install NLTK for advanced features!", "mood")
    
    def add_message(self, sender, message, tag=""):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        if sender == "You":
            prefix = f"[{timestamp}] 👤 You: "
            self.chat_display.insert(tk.END, prefix, "user")
        elif sender == "ChatBot":
            prefix = f"[{timestamp}] 🤖 ChatBot: "
            self.chat_display.insert(tk.END, prefix, "bot")
        else:
            prefix = f"[{timestamp}] ℹ️ {sender}: "
            self.chat_display.insert(tk.END, prefix, "timestamp")
        
        self.chat_display.insert(tk.END, f"{message}\n\n", tag)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Update message count
        count = len(self.conversation_history)
        self.message_count_label.config(text=f"Messages: {count}")
    
    def send_message(self):
        """Process and send user message"""
        user_text = self.user_input.get("1.0", tk.END).strip()
        if not user_text:
            return
        
        # Add user message to display
        self.add_message("You", user_text, "user")
        
        # Clear input
        self.user_input.delete("1.0", tk.END)
        
        # Process in background thread
        threading.Thread(target=self.process_message, args=(user_text,), daemon=True).start()
        
        # Update status
        self.status_label.config(text="🤔 ChatBot thinking...", fg=self.colors['warning'])
    
    def process_message(self, user_text):
        """Process user message and generate response"""
        try:
            # Store conversation
            self.conversation_history.append({
                'user': user_text,
                'timestamp': datetime.datetime.now(),
                'mood': self.detect_mood(user_text) if NLTK_AVAILABLE and self.bot_settings['mood_detection'] else None
            })
            
            # Analyze user input
            analysis = self.analyze_input(user_text)
            
            # Generate response
            response = self.generate_response(user_text, analysis)
            
            # Add response to chat
            self.root.after(0, lambda: self.add_message("ChatBot", response, "bot"))
            
            # Store bot response
            self.conversation_history[-1]['bot'] = response
            
            # Update learning
            if self.bot_settings['learning_mode']:
                self.update_learning(user_text, analysis)
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="🟢 ChatBot Ready", fg=self.colors['success']))
            
        except Exception as e:
            error_msg = "Sorry, I encountered an error processing your message. Please try again!"
            self.root.after(0, lambda: self.add_message("ChatBot", error_msg, "bot"))
            self.root.after(0, lambda: self.status_label.config(text="⚠️ Error occurred", fg=self.colors['error']))
    
    def analyze_input(self, text):
        """Analyze user input for patterns and intent"""
        analysis = {
            'categories': [],
            'keywords': [],
            'sentiment': None,
            'intent': 'unknown',
            'entities': []
        }
        
        text_lower = text.lower()
        
        # Check knowledge base patterns
        for category, data in self.knowledge_base.items():
            if category == 'default':
                continue
                
            for pattern in data.get('patterns', []):
                if re.search(pattern, text_lower):
                    analysis['categories'].append(category)
                    break
        
        # Extract keywords (if NLTK available)
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text_lower)
                keywords = [self.lemmatizer.lemmatize(word) for word in tokens 
                           if word.isalpha() and word not in self.stop_words]
                analysis['keywords'] = keywords[:10]  # Top 10 keywords
                
                # Sentiment analysis
                if self.bot_settings['mood_detection']:
                    analysis['sentiment'] = self.detect_mood(text)
                    
            except Exception:
                pass
        
        # Simple entity detection
        entities = []
        # Detect names (capitalized words that aren't at sentence start)
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and i > 0 and words[i-1][-1] not in '.!?':
                entities.append(word)
        analysis['entities'] = entities
        
        # Determine intent
        if analysis['categories']:
            analysis['intent'] = analysis['categories'][0]
        elif any(word in text_lower for word in ['?', 'what', 'how', 'why', 'when', 'where']):
            analysis['intent'] = 'question'
        elif any(word in text_lower for word in ['please', 'can you', 'could you', 'help']):
            analysis['intent'] = 'request'
        
        return analysis
    
    def generate_response(self, user_text, analysis):
        """Generate appropriate response based on analysis"""
        # Check for specific patterns first
        if analysis['categories']:
            category = analysis['categories'][0]
            if category in self.knowledge_base:
                responses = self.knowledge_base[category]['responses']
                base_response = random.choice(responses)
                
                # Customize based on personality
                return self.customize_response(base_response, analysis)
        
        # Check for advanced topics
        for topic, responses in self.advanced_topics.items():
            if any(keyword in user_text.lower() for keyword in [topic]):
                base_response = random.choice(responses)
                return self.customize_response(base_response, analysis)
        
        # Handle user name detection and storage
        if not self.user_profile['name'] and any(word in user_text.lower() for word in ['my name is', 'i am', "i'm"]):
            name = self.extract_name(user_text)
            if name:
                self.user_profile['name'] = name
                return f"Nice to meet you, {name}! 😊 I'll remember your name for our future conversations."
        
        # Use name if available
        name_prefix = f"{self.user_profile['name']}, " if self.user_profile['name'] else ""
        
        # Generate contextual response
        if analysis['intent'] == 'question':
            responses = [
                f"{name_prefix}That's a great question! 🤔 While I don't have specific data on that, I'd love to explore the topic with you.",
                f"{name_prefix}Interesting question! 💭 What specifically about this topic would you like to discuss?",
                f"{name_prefix}I appreciate your curiosity! 🌟 Let me think about that..."
            ]
        elif analysis['intent'] == 'request':
            responses = [
                f"{name_prefix}I'd be happy to help! 🤝 Could you provide more details about what you need?",
                f"{name_prefix}Of course! 💪 Tell me more about what assistance you're looking for.",
                f"{name_prefix}I'm here to help! 🎯 What specifically can I do for you?"
            ]
        else:
            # Use default responses
            responses = self.knowledge_base['default']
        
        base_response = random.choice(responses)
        return self.customize_response(base_response, analysis)
    
    def customize_response(self, base_response, analysis):
        """Customize response based on personality and mood"""
        response = base_response
        
        # Add mood acknowledgment if available
        if analysis.get('sentiment') and self.bot_settings['mood_detection']:
            mood = analysis['sentiment']
            if mood['compound'] < -0.5:
                response = f"I sense you might be feeling down. 💙 {response}"
            elif mood['compound'] > 0.5:
                response = f"I can feel your positive energy! ✨ {response}"
        
        # Adjust for personality
        personality = self.bot_settings['personality']
        
        if personality == 'professional':
            response = response.replace('!', '.').replace('😊', '').replace('🤗', '')
        elif personality == 'humorous':
            jokes = [" (I crack myself up! 😄)", " *virtual dad joke incoming*", " (That's my attempt at humor! 🤪)"]
            if random.random() < 0.3:  # 30% chance to add humor
                response += random.choice(jokes)
        elif personality == 'technical':
            if any(word in response.lower() for word in ['technology', 'programming', 'code']):
                response += " Would you like to dive deeper into the technical aspects?"
        
        # Adjust for response style
        style = self.bot_settings['response_style']
        if style == 'brief':
            # Shorten response
            response = response.split('.')[0] + '.'
        elif style == 'creative':
            # Add creative elements
            if random.random() < 0.4:
                creative_additions = [
                    " ✨ Life is full of interesting conversations!",
                    " 🌈 Every chat teaches me something new!",
                    " 🚀 Our conversation is taking off!"
                ]
                response += random.choice(creative_additions)
        
        return response
    
    def detect_mood(self, text):
        """Detect mood using sentiment analysis"""
        if not NLTK_AVAILABLE:
            return None
            
        try:
            scores = self.sentiment_analyzer.polarity_scores(text)
            return scores
        except Exception:
            return None
    
    def extract_name(self, text):
        """Extract user name from text"""
        patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"i'm (\w+)",
            r"call me (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).title()
        return None
    
    def update_learning(self, user_text, analysis):
        """Update bot's learning from conversation"""
        # Track topics discussed
        for keyword in analysis.get('keywords', []):
            self.user_profile['topics_discussed'][keyword] += 1
        
        # Store mood history
        if analysis.get('sentiment'):
            self.user_profile['mood_history'].append({
                'timestamp': datetime.datetime.now(),
                'sentiment': analysis['sentiment']
            })
            
            # Keep only last 50 mood entries
            if len(self.user_profile['mood_history']) > 50:
                self.user_profile['mood_history'].pop(0)
    
    def update_personality(self):
        """Update bot personality"""
        self.bot_settings['personality'] = self.personality_var.get()
        self.add_message("System", f"🎭 Personality updated to: {self.personality_var.get().title()}", "mood")
    
    def update_style(self):
        """Update response style"""
        self.bot_settings['response_style'] = self.style_var.get()
        self.add_message("System", f"✍️ Response style updated to: {self.style_var.get().title()}", "mood")
    
    def toggle_learning(self):
        """Toggle learning mode"""
        self.bot_settings['learning_mode'] = self.learning_var.get()
        status = "enabled" if self.learning_var.get() else "disabled"
        self.add_message("System", f"🧠 Learning mode {status}", "mood")
    
    def toggle_mood_detection(self):
        """Toggle mood detection"""
        self.bot_settings['mood_detection'] = self.mood_var.get()
        status = "enabled" if self.mood_var.get() else "disabled"
        self.add_message("System", f"💭 Mood detection {status}", "mood")
    
    def update_statistics(self):
        """Update and display statistics"""
        stats = self.generate_statistics()
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", stats)
        self.stats_text.config(state=tk.DISABLED)
    
    def generate_statistics(self):
        """Generate conversation statistics"""
        total_messages = len(self.conversation_history)
        
        if total_messages == 0:
            return "📊 No conversation data yet!\n\nStart chatting to see statistics."
        
        # Calculate statistics
        user_messages = sum(1 for msg in self.conversation_history if 'user' in msg)
        
        # Most discussed topics
        top_topics = sorted(self.user_profile['topics_discussed'].items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        
        # Average mood (if available)
        avg_mood = "N/A"
        if self.user_profile['mood_history'] and NLTK_AVAILABLE:
            mood_scores = [m['sentiment']['compound'] for m in self.user_profile['mood_history']]
            avg_score = sum(mood_scores) / len(mood_scores)
            if avg_score > 0.1:
                avg_mood = "😊 Positive"
            elif avg_score < -0.1:
                avg_mood = "😔 Negative"
            else:
                avg_mood = "😐 Neutral"
        
        # Session duration
        if self.conversation_history:
            session_start = self.conversation_history[0]['timestamp']
            session_duration = datetime.datetime.now() - session_start
            duration_str = str(session_duration).split('.')[0]  # Remove microseconds
        else:
            duration_str = "0:00:00"
        
        stats = f"""📊 Conversation Statistics

💬 Total Messages: {total_messages}
👤 Your Messages: {user_messages}
🤖 Bot Responses: {total_messages - user_messages}

⏱️ Session Duration: {duration_str}
👤 Your Name: {self.user_profile['name'] or 'Not provided'}

😊 Average Mood: {avg_mood}

🔥 Top Discussion Topics:
"""
        
        if top_topics:
            for i, (topic, count) in enumerate(top_topics, 1):
                stats += f"{i}. {topic.title()} ({count} mentions)\n"
        else:
            stats += "No topics tracked yet.\n"
        
        stats += f"""
🎭 Current Personality: {self.bot_settings['personality'].title()}
✍️ Response Style: {self.bot_settings['response_style'].title()}
🧠 Learning Mode: {'On' if self.bot_settings['learning_mode'] else 'Off'}
💭 Mood Detection: {'On' if self.bot_settings['mood_detection'] else 'Off'}

🔧 NLTK Features: {'Available' if NLTK_AVAILABLE else 'Not Available'}
"""
        
        return stats
    
    def insert_template(self, template):
        """Insert template text into input field"""
        self.user_input.delete("1.0", tk.END)
        self.user_input.insert("1.0", template)
        self.user_input.focus_set()
        self.user_input.mark_set(tk.INSERT, tk.END)
    
    def clear_chat(self):
        """Clear chat history"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            self.conversation_history.clear()
            self.message_count_label.config(text="Messages: 0")
            
            # Re-greet user
            self.greet_user()
    
    def export_conversation(self):
        """Export conversation to file"""
        if not self.conversation_history:
            messagebox.showwarning("Export", "No conversation to export!")
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="Export Conversation",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    # Export as JSON
                    export_data = {
                        'conversation': self.conversation_history,
                        'user_profile': self.user_profile,
                        'bot_settings': self.bot_settings,
                        'export_timestamp': datetime.datetime.now().isoformat()
                    }
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, default=str)
                else:
                    # Export as text
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("🤖 ChatBot Conversation Export\n")
                        f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for msg in self.conversation_history:
                            timestamp = msg['timestamp'].strftime('%H:%M:%S')
                            f.write(f"[{timestamp}] You: {msg['user']}\n")
                            if 'bot' in msg:
                                f.write(f"[{timestamp}] ChatBot: {msg['bot']}\n")
                            f.write("\n")
                
                messagebox.showinfo("Export", f"Conversation exported successfully!\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export conversation:\n{str(e)}")
    
    def on_enter(self, event):
        """Handle Enter key press"""
        if event.state & 0x1:  # Shift is pressed
            return  # Allow newline
        else:
            self.send_message()
            return "break"  # Prevent default behavior
    
    def on_shift_enter(self, event):
        """Handle Shift+Enter for newline"""
        return  # Allow default behavior (newline)

def main():
    """Run the chatbot application"""
    root = tk.Tk()
    app = AdvancedChatBot(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
