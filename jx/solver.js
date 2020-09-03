String.prototype.sort = function() { return this.split('').sort(); };
$ = x => document.querySelector(x);
$$ = x => document.querySelectorAll(x);

ALL_WORDS = [];
ALL_DICT = {};

[1, 2, 3].forEach(i => {
    fetch(`owl2018_0${i}.txt`).then(resp => resp.text()).then(owl => {
        owl.match(/\w+/g).forEach(word => {
            ALL_WORDS.push(word);
            ALL_DICT[word] = true;
        });
    });
});

hash = word => word.sort().join('');

cell = (str, cls, word, addHash) => ( `<cell
    class="${cls || ''}"
    ${word?`data-word="${word}"`:''}
    ${addHash?`data-hash="${hash(word)}"`:''}
>${str}</cell>`);

handleFind = (hidden) => {
    var input = $('#input').value.toUpperCase(),
        found = [],
        res = [],
        output = '',
        regex,
        clauses;

    if(!input) return;

    [regex, ...clauses] = input.match(/([^ ]+)/g);

    regex = regex.replace('@', '(.+)');
    regex = `^(?:${regex})$`;

    ALL_WORDS.forEach(word => {
        if(matches = word.match(regex)) {
            found.push(matches);
        }
    });

    res = found.filter(matches => (
        clauses.every(clause => {
            var word = clause.replace(/\d/g, x => matches[x | 0]);
            if (len = clause.match(/^<(\d+)$/)) {
                return matches[0].length < (len[1] | 0);
            } else if (len = clause.match(/^>(\d+)$/)) {
                return matches[0].length > (len[1] | 0);
            } else {
                return ALL_DICT[word];
            }
        })
    )).map(x => x[0]);

    output += res.map(x => cell(x, hidden? hidden: '', x, 1)).join('');

    $('#answer').innerHTML = output || cell('No solution!');
    if(hidden) {
        $('#input').value = '';
    }
    $('#input').focus();
    $("#count").innerHTML = $$('cell').length;

};

handleInput = (event) => {
    var input = $('#input').value.toUpperCase();

    input = input.replace(/^ +| +$/g, '');

    if (event.keyCode == 13) {
        if(!input)
            return false;
        if($el = $(`cell[data-word="${input}"]`)) {
            $el.classList.remove('hidden');
            $el.classList.add('got');
            $("#count").innerHTML = $$('cell.hidden').length;
        }
        else {
            $('#answer').innerHTML += cell(input, 'err');
        }
        $('#input').value = '';
        return false;
    }
};

handleReveal = () => {
    $$('cell.hidden').forEach($el => {
        $el.classList.remove('hidden');
        $el.classList.add('missed');
    });
};

handleClear = () => {
    $('#answer').innerHTML = '';
    $('#input').value = '';
    $('#input').focus();
    $("#count").innerHTML = '';
};
