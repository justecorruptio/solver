String.prototype.sort = function() { return this.split('').sort(); };
$ = x => document.querySelector(x);
$$ = x => document.querySelectorAll(x);

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

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

DEFS = {};

fetch('def.txt').then(resp => resp.text()).then(file => {
    file.match(/[^\n]+\n/g).forEach(line => {
        var [words, def] = line.split('\t');
        words.split(' ').forEach(word => {
            DEFS[word.toUpperCase()] = def;
        });
    });
});

ulu = (pattern) => {
    var count = 0,
        any = false;

    pattern = pattern.replace(/[?]/g, x=>(count++, ''));
    pattern = pattern.replace(/[@]/g, x=>(any=true, ''));
    pattern = new RegExp(['^', ...pattern.sort(), '$'].join('(.*)'), 'i');

    return (word) => {
        var hx = hash(word),
            result = hx.replace(pattern, (...v)=>v.slice(1,-2).join(''));

        if (result != hx && (any || result.length == count)) {
            return [word];
        }
        return null;
    }
}

hash = word => word.sort().join('');

cell = (str, cls, word, addHash) => ( `<cell
    class="${cls || ''}"
    ${word?`data-word="${word}"`:''}
    ${addHash?`data-hash="${hash(word)}"`:''}
    onclick="handleClickCell(event)"
>${str}</cell>`);

annotate = (word) => {
    var pre = '',
        post = '',
        preDel = '',
        postDel = '',
        hidden;

    LETTERS.forEach((l) => {
        if (ALL_DICT[l + word]) {
            pre += l;
        }
        if (ALL_DICT[word + l]) {
            post += l;
        }
    });

    if(ALL_DICT[word.substring(1)]) {
        preDel = '●';
    }

    if(ALL_DICT[word.substring(0, word.length - 1)]) {
        postDel = '●';
    }

    hidden = $('#checkAnnotate').checked ? '': 'hidden';

    return `
        <small class="annotation ${hidden}">${pre}${preDel}</small>
        ${word}
        <small class="annotation ${hidden}">${postDel}${post}</small>
    `;
}

handleFind = (type) => {
    var input = $('#input').value.toUpperCase(),
        found = [],
        res = [],
        output = '',
        regex,
        clauses,
        classes = '',
        match_func;

    if(!input) return;

    [regex, ...clauses] = input.match(/([^ \/]+)/g);


    if ($('#checkRegex').checked) {
        regex = regex.replace(/@/g, '(.+)');
        regex = `^(?:${regex})$`;
        match_func = (word) => word.match(regex);
    } else {
        match_func = ulu(regex);
    }

    ALL_WORDS.forEach(word => {
        if(matches = match_func(word)) {
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
            } else if (len = clause.match(/^=(\d+)$/)) {
                return matches[0].length == (len[1] | 0);
            } else {
                return ALL_DICT[word];
            }
        })
    )).map(x => x[0]);

    if (type == 'blur') {
        classes = 'blur hidden';
    }
    else if (type == 'alpha') {
        classes = 'alpha hidden';
        res.sort((a, b) => (`${a.length}`.padStart(2, '0') + hash(a) > `${b.length}`.padStart(2, '0') + hash(b)));
    }

    output += res.map(x => cell(annotate(x), classes, x, 1)).join('');

    $('#answer').innerHTML = output || cell('No solution!');

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
            $$('.last-got').forEach(x=>x.classList.remove('last-got'));
            $el.classList.add('last-got');
            $("#count").innerHTML = $$('cell.hidden').length;
        } else if (ALL_DICT[input]) {
            $('#answer').innerHTML += cell(input, 'err good');
        } else {
            $('#answer').innerHTML += cell(input, 'err');
        }
        $('#input').value = '';
        return false;
    }
};

handleAnnotation = (event) => {
    $$('.annotation').forEach(x => x.classList.toggle('hidden'));
}

handleFocus = (event, height) => {
    let vh = window.innerHeight - height;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
};

handleReveal = () => {
    $$('cell.hidden').forEach($el => {
        $el.classList.remove('hidden');
        $el.classList.add('missed');
    });
};

handleClickCell = (event) => {
    var attr = event.target.attributes['data-word'];
    if(attr) {
        showDef(attr.value);
    }
}

showDef = (word) => {
    $('#def').innerText = DEFS[word] || 'No definition';
    $('#def').style.display = 'block';
}
