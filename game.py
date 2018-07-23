game_template = """
    <div class="container">
        <div class="row">
            <div class="col-sm-6 mt-2">
                <h4>
                    Score:
                    <span id="curr_score" class="text-success">0</span>
                    Time Left:
                    <span id="time_left" class="text-danger">1000</span>
                </h4>
            </div>
            <div class="col-sm-12 text-center">
                <h2>
                    <div id="question">Play!</div>
                </h2>
            </div>
            <div class="col-sm-12 mt-3 text-center">
                <input
                    class="form-control text-center text-uppercase"
                    id="input"
                    style="font-size: 30px; display: none;"
                    autofocus
                >
                <button id="start" type="button" class="btn btn-primary">Begin!</button>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-12 text-center">
                <h5 class="mt-3">High Scores</h5>
                <table class="table">
                    <tbody id="score_table">
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script
        src="https://code.jquery.com/jquery-3.3.1.min.js"
        integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="
        crossorigin="anonymous"
    ></script>
    <script>
        var $curr_score = $('#curr_score');
        var $time_left = $('#time_left');
        var $input = $('#input');
        var $start = $('#start');
        var $question = $('#question');
        var interval = 0;
        var curr_score = 0;
        var time_upper = time_left = 1000;
        var my_token = '';

        var $score_table = $('#score_table');
        var high_scores = [];

        var query = () => {
            $.post('#', {
                curr_score,
                time_left,
                time_upper,
                my_token,
                input: $input.val(),
                question: $question.text(),
            }, null, 'json').done(({score, question, new_time_upper, token}) => {
                $curr_score.text(curr_score = score);
                $time_left.text(time_upper = time_left = new_time_upper)
                my_token = token,
                $question.text(question);
                $input.removeClass('is-invalid').addClass('is-valid');
            }).fail(() => {
                $input.removeClass('is-valid').addClass('is-invalid');
            }).always(() => {
                $input.val('');
                setTimeout(() => {$input.removeClass('is-valid is-invalid');}, 1000);
            });
        };

        var get_scores = () => {
            return $.get('game/scores', {}, null, 'json').done((scores) => {
                high_scores = scores;

                $score_table.empty();
                high_scores.forEach(({name, score}) => {
                    $score_table.append($(`<tr><td>${name}</td><td>${score}</td></tr>`));
                });
            });
        }

        var set_scores = () => {
            var name = window.prompt('New High Score!, Enter you name') || 'Anonymous';
            return $.post('game/scores', {
                name,
                my_token,
            }, null, 'json');
        }

        var game_end = () => {
            get_scores().done(() => {
                if(curr_score < high_scores[high_scores.length - 1].score) {
                    return;
                }
                set_scores().done(get_scores);
                my_token = '';
            });
        };

        $start.click(() => {
            curr_score = 0;
            time_left = 1000;
            $start.hide();
            $input.show().focus();

            interval = setInterval(() => {
                $time_left.text(--time_left);
                if(time_left == 0) {
                    clearInterval(interval);
                    interval = 0;
                    $start.show();
                    $input.hide();
                    $question.text('Game Over.');
                    game_end();
                }
            }, 50);
            query();
        });

        $input.keypress((e) => {
            if(e.which != 13) {
                return true;
            }
            query();
        });

        $(() => {
            get_scores();
        });
    </script>
""".replace('{', '{{').replace('}', '}}')
