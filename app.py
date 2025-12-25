import streamlit as st
import json
import random
import time

# Page Config
st.set_page_config(page_title="Holiday Dilemmas", page_icon="🎄", layout="centered")

# --- CSS Injection ---
def load_css():
    # Load fonts and raw CSS
    st.markdown("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@400;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    with open('static/style.css', 'r') as f:
        css = f.read()
    
    # Adapt CSS for Streamlit structure & Overrides
    # Remove the problematic nested <style> tags from the previous implementation
    css += """
        /* Streamlit App Background */
        .stApp {
            background-color: #2F5233; /* Christmas Green */
            background-image: repeating-linear-gradient(
                45deg,
                #2F5233,
                #2F5233 20px,
                #1A3C23 20px,
                #1A3C23 40px
            );
        }
        
        .main .block-container {
            max-width: 650px;
            padding: 3rem 1rem;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 8px solid #D42426;
            margin-top: 2rem;
        }

        /* Hide standard Streamlit elements */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Headers */
        h1 {
            font-family: 'Mountains of Christmas', cursive !important;
            color: #D42426 !important;
            font-size: 5rem !important;
            text-align: center;
            text-shadow: 3px 3px 0px #F1D570;
            margin-bottom: 0 !important;
        }
        
        h2, h3 {
            font-family: 'Mountains of Christmas', cursive !important;
            color: #D42426 !important;
            font-size: 3.5rem !important;
            text-shadow: 2px 2px 0px #F1D570;
            margin-bottom: 1rem !important;
            text-align: center;
        }
        
        .subtitle {
            font-family: 'Roboto', sans-serif;
            color: #2F5233;
            text-align: center;
            font-size: 1.5rem;
            margin-bottom: 2rem;
            font-style: italic;
        }

        /* Inputs */
        div[data-baseweb="input"] {
            border-radius: 12px !important;
            border: 2px solid #F1D570 !important;
            background-color: #fff !important;
        }
        div[data-baseweb="input"] input {
            font-family: 'Mountains of Christmas', cursive !important;
            font-size: 2.2rem !important;
            color: #1A3C23 !important; /* Dark Green Text */
            caret-color: #D42426;
        }
        /* Reliable Streamlit Label Targeting */
        label, 
        .stTextInput label, 
        div[data-testid="stWidgetLabel"] p,
        div[data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
            font-size: 2rem !important;
            font-family: 'Mountains of Christmas', cursive !important;
            text-shadow: 2px 2px 0px #1A3C23; /* Dark shadow for legibility */
            margin-bottom: 0.5rem !important;
        }

        /* Custom Buttons */
        .stButton button {
            background: linear-gradient(to bottom, #D42426, #B31B1D) !important;
            color: #FFF !important;
            border: 3px solid #F1D570 !important;
            font-family: 'Mountains of Christmas', cursive !important;
            font-size: 2.2rem !important;
            border-radius: 50px !important;
            padding: 1rem 2.5rem !important;
            transition: transform 0.2s, box-shadow 0.2s !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
        }
        .stButton button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;
            border-color: #FFF !important;
        }
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# --- Game Logic ---
def load_questions():
    try:
        with open('questions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return ["Error: questions.json not found!"]

def init_game():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'SETUP' # SETUP, PREDICT, PASS, ANSWER, RESULT, WINNER
        st.session_state.players = []
        st.session_state.current_reader_idx = 0
        st.session_state.current_target_idx = 1
        st.session_state.questions = load_questions()
        st.session_state.current_question = None
        st.session_state.prediction = None
        st.session_state.winning_score = 3 # Short game for quick fun

def next_turn():
    total_players = len(st.session_state.players)
    st.session_state.current_reader_idx = (st.session_state.current_reader_idx + 1) % total_players
    st.session_state.current_target_idx = (st.session_state.current_reader_idx + 1) % total_players
    st.session_state.current_question = random.choice(st.session_state.questions)
    st.session_state.game_state = 'PREDICT'
    st.rerun()

def start_game(player_names):
    valid_players = [name.strip() for name in player_names if name.strip()]
    if len(valid_players) < 2:
        st.error("Need at least 2 players!")
        return
    
    st.session_state.players = [{'name': name, 'score': 0} for name in valid_players]
    st.session_state.current_question = random.choice(st.session_state.questions)
    st.session_state.game_state = 'PREDICT'
    st.rerun()

def submit_prediction(vote):
    st.session_state.prediction = vote
    st.session_state.game_state = 'PASS'
    st.rerun()

def submit_answer(vote):
    reader = st.session_state.players[st.session_state.current_reader_idx]
    correct = (vote == st.session_state.prediction)
    
    if correct:
        reader['score'] += 1
        st.session_state.last_result = f"Correct! {reader['name']} gets a point."
        st.session_state.result_color = "var(--gold)"
    else:
        st.session_state.last_result = "Wrong! No points."
        st.session_state.result_color = "#ffcccc"
        
    if reader['score'] >= st.session_state.winning_score:
        st.session_state.game_state = 'WINNER'
        st.session_state.winner = reader['name']
    else:
        st.session_state.game_state = 'RESULT'
    st.rerun()

# --- UI Components ---
def render_header():
    st.markdown("""
        <header>
            <h1>Holiday Dilemmas</h1>
            <p class="subtitle">A game of Scruples for the festive season</p>
        </header>
    """, unsafe_allow_html=True)

def render_scoreboard():
    cols = st.columns(len(st.session_state.players))
    for i, player in enumerate(st.session_state.players):
        is_active = (i == st.session_state.current_reader_idx)
        active_class = "active" if is_active else ""
        with cols[i]:
            st.markdown(f"""
                <div class="player-score {active_class}">
                    <span class="score-name">{player['name']}</span>
                    <span class="score-value">{player['score']}</span>
                </div>
            """, unsafe_allow_html=True)

def render_card(text):
    st.markdown(f"""
        <div class="card-container">
            <div class="card">
                <p>{text}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Main App ---
def main():
    load_css()
    init_game()
    
    # Snowflakes
    st.markdown("""
        <div class="snowflakes" aria-hidden="true">
            <div class="snowflake">❅</div><div class="snowflake">❆</div>
            <div class="snowflake">❅</div><div class="snowflake">❆</div>
            <div class="snowflake">❅</div><div class="snowflake">❆</div>
            <div class="snowflake">❅</div><div class="snowflake">❆</div>
            <div class="snowflake">❅</div><div class="snowflake">❆</div>
        </div>
    """, unsafe_allow_html=True)

    render_header()

    if st.session_state.game_state == 'SETUP':
        st.markdown("## Who is playing?")
        name1 = st.text_input("Player 1 Name")
        name2 = st.text_input("Player 2 Name")
        name3 = st.text_input("Player 3 Name (Optional)")
        name4 = st.text_input("Player 4 Name (Optional)")
        
        if st.button("Start Game"):
            start_game([name1, name2, name3, name4])

    elif st.session_state.game_state == 'WINNER':
        st.markdown(f"<h2 id='winner-message'>{st.session_state.winner} Wins the Game!</h2>", unsafe_allow_html=True)
        st.balloons()
        if st.button("Play Again"):
            st.session_state.game_state = 'SETUP'
            st.rerun()
            
    else:
        # Game Screens
        render_scoreboard()
        
        reader = st.session_state.players[st.session_state.current_reader_idx]['name']
        target = st.session_state.players[st.session_state.current_target_idx]['name']
        
        st.markdown(f"""
            <div class="turn-indicator">
                <span class="highlight">{reader}</span> is asking <span class="highlight">{target}</span>
            </div>
        """, unsafe_allow_html=True)
        
        render_card(st.session_state.current_question)
        
        st.markdown('<div class="interaction-zone">', unsafe_allow_html=True)
        
        if st.session_state.game_state == 'PREDICT':
            st.markdown(f'<p class="instruction">{reader}, how will {target} answer?</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if c1.button("YES"): submit_prediction("yes")
            if c2.button("NO"): submit_prediction("no")
            if c3.button("DEPENDS"): submit_prediction("depends")
            
        elif st.session_state.game_state == 'PASS':
            st.markdown(f'<p class="instruction">Pass the device to {target}!</p>', unsafe_allow_html=True)
            if st.button(f"I am {target}"):
                st.session_state.game_state = 'ANSWER'
                st.rerun()
                
        elif st.session_state.game_state == 'ANSWER':
            st.markdown(f'<p class="instruction">{target}, be honest...</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            if c1.button("YES"): submit_answer("yes")
            if c2.button("NO"): submit_answer("no")
            if c3.button("DEPENDS"): submit_answer("depends")
            
        elif st.session_state.game_state == 'RESULT':
             st.markdown(f"""
                <p class="result-text" style="color: {st.session_state.result_color}">
                    {st.session_state.last_result}
                </p>
            """, unsafe_allow_html=True)
             if st.button("Next Turn"):
                 next_turn()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
