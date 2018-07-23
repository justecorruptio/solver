game_template = """
    <div class="container">
        <div class="row">
            <div class="col-sm-6">
                <h4>
                    Score:
                    <span id="curr_score" class="text-success">0</span>
                    Time Left:
                    <span id="time_left" class="text-danger">1000</span>
                </h4>
            </div>
            <div class="col-sm-12 text-center">
                <h2>
                    <div id="question">Practice!</div>
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

        var query = () => {
            $.post('#', {
                curr_score,
                time_left,
                time_upper,
                input: $input.val(),
                question: $question.text(),
            }, null, 'json').done(({score, question, new_time_upper}) => {
                $curr_score.text(curr_score = score);
                $time_left.text(time_upper = time_left = new_time_upper)
                $question.text(question);
                $input.removeClass('is-invalid').addClass('is-valid');
            }).fail(() => {
                $input.removeClass('is-valid').addClass('is-invalid');
            }).always(() => {
                $input.val('');
                setTimeout(() => {$input.removeClass('is-valid is-invalid');}, 1000);
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
    </script>
""".replace('{', '{{').replace('}', '}}')
