header = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/css/bootstrap.min.css" integrity="sha384-Smlep5jCw/wG7hdkwQ/Z5nLIefveQRIY9nfy6xoR1uRYBtpZgI6339F5dgvm/e9B" crossorigin="anonymous">
        <style>
            textarea {{
                min-height: 150px !important;
                resize: vertical !important;
            }}
            .mono {{
                font-family: "Menlo", "Lucida Console", Monaco, monospace;
            }}
        </style>
    </head>
    <body>
    <div class="container-fluid">
"""

footer = """
    </div>
    </body></html>
"""

timed_footer = """
    <div class="row" id="small">
        <div class="col-sm-12 mt-5">
            <small>Generated in {elapsed:0.4f} secs.</small>
        </div>
    </div>

    </div>
    </body></html>
"""

index_template = """
    <div class="row">
    <div class="col-sm-12"><h3>Anagram/Snatch Solver</h3></div>
    <div class="col-sm-12">
        <form id="qform" action="" method="post">
            <div class="form-group">
            <textarea class="form-control" name="q" autofocus>{form_q}</textarea>
            </div>
            <div class="form-group">
            <button class="btn btn-primary" type="submit">Solve!</button>
            <a class="btn btn-secondary" href="">Clear</a>
            </div>
        </form>
    </div>

    </div>
    <div class="row">{rows}</div>

"""

test_template = """
    <div class="row mono">
    <div class="col-sm-12"><h3>Scrabble Test: {query}</h3></div>
    <div class="col-sm-12">
        <form id="qform" action="" method="post">
            <div class="form-group">
            <textarea class="form-control" name="q" rows="10" autofocus>{form_q}</textarea>
            </div>
            <div class="form-group">
            <button class="btn btn-primary" type="submit">Check!</button>
            <a class="btn btn-secondary" href="">Reset</a>
            </div>
        </form>
    </div>

    </div>
    <div class="row mono">{rows}</div>
"""
