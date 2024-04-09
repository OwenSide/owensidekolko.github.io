from flask import Flask, render_template ,redirect, url_for
import sqlite3

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key'  

conn = sqlite3.connect('tic_tac_toe.db')
cursor = conn.cursor()
with app.open_resource('schema.sql', mode='r') as f:
    cursor.executescript(f.read())
conn.commit()
conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new_game')
def new_game():
    conn = sqlite3.connect('tic_tac_toe.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO games (board, winner) VALUES (?, ?)", ('-' * 9, ''))
    game_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return redirect(url_for('play', game_id=game_id))


def get_move_symbol(moves, position):
    for move in moves:
        if move[1] == position:
            return move[0]
    return '-'


@app.route('/play/<int:game_id>')
def play(game_id):
    conn = sqlite3.connect('tic_tac_toe.db')
    cursor = conn.cursor()
    cursor.execute("SELECT board, winner FROM games WHERE id=?", (game_id,))
    result = cursor.fetchone()
    board, winner = result[0], result[1]

    cursor.execute("SELECT player, position FROM moves WHERE game_id=?", (game_id,))
    moves = cursor.fetchall()

    conn.close()

    return render_template('play.html', game_id=game_id, board=board, winner=winner, moves=moves, get_move_symbol=get_move_symbol)


@app.route('/make_move/<int:game_id>/<int:position>')
def make_move(game_id, position):
    conn = sqlite3.connect('tic_tac_toe.db')
    cursor = conn.cursor()
    cursor.execute("SELECT board, winner FROM games WHERE id=?", (game_id,))
    result = cursor.fetchone()
    board, winner = result[0], result[1]

    if winner == '' and board[position] == '-':
        player_query = cursor.execute("SELECT player FROM moves WHERE game_id=?", (game_id,))
        player = 'X' if len([p for p in player_query]) % 2 == 0 else 'O'

        board = board[:position] + player + board[position + 1:]
        cursor.execute("UPDATE games SET board=? WHERE id=?", (board, game_id))

        cursor.execute("INSERT INTO moves (game_id, move_number, player, position) VALUES (?, ?, ?, ?)",
                       (game_id, len([m for m in cursor.execute("SELECT move_number FROM moves WHERE game_id=?", (game_id,))]) + 1, player, position))

        if check_winner(board, player):
            cursor.execute("UPDATE games SET winner=? WHERE id=?", (player, game_id))
        elif '-' not in board:
            cursor.execute("UPDATE games SET winner=? WHERE id=?", ('Draw', game_id))

        conn.commit()
        conn.close()

    return redirect(url_for('play', game_id=game_id))



def check_winner(board, player):
    winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] == player:
            return True
    return False


if __name__ == '__main__':
    app.run(debug=True)