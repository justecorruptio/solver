String.prototype.sort = function() { return this.split('').sort(); };
String.prototype.zlength = function() { return `${this.length}`.padStart(2, '0') };
DOMTokenList.prototype._add = DOMTokenList.prototype.add;
DOMTokenList.prototype.add = function(v) {this._add(v); return this;}

DOMTokenList.prototype._remove = DOMTokenList.prototype.remove;
DOMTokenList.prototype.remove = function(v) {this._remove(v); return this;}

$ = x => document.querySelector(x);
$$ = x => document.querySelectorAll(x);

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

LOADED = 0;
check_load = () => {
    LOADED ++;
    if(LOADED == 3) {
        $('#input').disabled = false;
    }
}

ALL = {};

fetch('nwl2023.txt').then(resp => resp.text()).then(owl => {
    owl.match(/\w+/g).forEach(word => {
        ALL[word.toUpperCase()] = true;
    });
    check_load();
});

DEFS = {};
POS = {};

fetch('def.txt').then(resp => resp.text()).then(file => {
    file.match(/[^\n]+\n/g).forEach(line => {
        var [_, words, def, pos] = line.match(/([^\t]+)\t([ A-Z]+([a-z]+)[^\n]+)\n/);
        words.toUpperCase().split(' ').forEach(word => {
            DEFS[word] = def;
            (POS[word] = POS[word] || {})[pos] = 1;
        });
    });
    check_load();
});

RANKS = {};

fetch('ranks.txt').then(resp => resp.text()).then(file => {
    file.match(/[^\n]+\n/g).forEach(line => {
        var [hx, rank] = line.split('\t');
        RANKS[hx] = rank | 0;
    });
    check_load();
});

ulu = (pattern) => {
    var count = 0,
        any = false;

    pattern = pattern.replace(/[?]/g, x=>(count++, ''));
    pattern = pattern.replace(/[@]/g, x=>(any=true, ''));
    pattern = new RegExp(['^', ...pattern.sort(), '$'].join('(.*)'), 'i');

    return (word) => {
        var result = hash(word).replace(pattern, (...v)=>v.slice(1,-2).join(''));
        if (any || result.length == count) {
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
        hidden,
        rank;

    LETTERS.forEach((l) => {
        if (ALL[l + word]) {
            pre += l;
        }
        if (ALL[word + l]) {
            post += l;
        }
    });

    if(ALL[word.substring(1)]) {
        preDel = '●';
    }

    if(ALL[word.substring(0, word.length - 1)]) {
        postDel = '●';
    }

    hidden = $('#checkAnnotate').checked ? '': 'hidden';
    rank = (RANKS[hash(word)] || 99999) / 1000;
    rank = rank < 15 ? '' : rank < 25 ? '★' : rank < 50 ? '★★' : '★★★';
    pos = Object.keys(POS[word] || {}).join('&nbsp;');

    return `
        <div class="annotation-container ${hidden}">
        <small class="annotation left">${pre}${preDel}</small>
        <small class="annotation rank">${rank}</small>
        ${word}
        <small class="annotation right">${postDel}${post}</small>
        <small class="annotation pos">${pos}</small>
        </div>
    `;
}

handleFind = (type) => {

    var input,
        found,
        res = [],
        output = '',
        regex,
        clauses,
        classes = '',
        match_func;

    input = $('#input').value = $('#input').value.replace(/^\s+|\s+$/g, '');
    input = input.toUpperCase();

    if(!input) return;

    if (input.match(/[^a-zA-Z ?@:]/)) {
        $('#checkRegex').checked = true;
    }

    [regex, ...clauses] = input.match(/([^ :]+)/g);

    if ($('#checkRegex').checked) {
        regex = regex.replace(/@/g, '(.+)');
        regex = `^(?:${regex})$`;
        match_func = (word) => word.match(regex);
    } else {
        match_func = ulu(regex);
    }

    found = Object.keys(ALL).map(match_func).filter(x=>x);

    res = found.filter(matches => (
        clauses.every(clause => {
            var word = clause.replace(/\d/g, x => matches[x | 0]),
                len;
            if (len = clause.match(/^<(\d+)$/)) {
                return matches[0].length <=(len[1] | 0);
            } else if (len = clause.match(/^>(\d+)$/)) {
                return matches[0].length >=(len[1] | 0);
            } else if (len = clause.match(/^=(\d+)$/)) {
                return matches[0].length == (len[1] | 0);
            } else if (clause.match(/^[?\-+]/)){
                return true
            } else {
                return ALL[word];
            }
        })
    )).map(x => x[0]);

    clauses.forEach(clause => {
        var arg;
        if (arg = clause.match(/^[?](\d+)$/)) {
            res.sort((a, b) => Math.random() > .5);
            res = res.slice(0, arg[1] | 0);
        }
        if (arg = clause.match(/^[\-](\d+)$/)) {
            res = res.filter(word => (RANKS[hash(word)] || 99999) <= (arg[1] | 0))
        }
        if (arg = clause.match(/^[+](\d+)$/)) {
            res = res.filter(word => (RANKS[hash(word)] || 99999) >= (arg[1] | 0))
        }
    })

    res.sort((a, b) => a.zlength() + a > b.zlength() + b);

    if (type == 'blur') {
        classes = 'blur hidden';
    }
    else if (type == 'alpha') {
        classes = 'alpha hidden';
        res.sort((a, b) => a.zlength() + hash(a) > b.zlength() + hash(b));
    }

    output += res.map(x => cell(annotate(x), classes, x, 1)).join('');

    $('#answer').innerHTML = output || cell('No solution!');

    $('#input').focus();
    $("#count").innerHTML = $$('cell').length;

    location.hash = ($('#checkRegex').checked?'R':'U') + ',' + input.replace(/ /g, ':');
};

getCell = ($el, success) => {
    $$('.last-got').forEach(x=>x.classList.remove('last-got'));
    $el.classList.remove('hidden').add(success?'got':'missed').add('last-got');
    $("#count").innerHTML = $$('cell.hidden').length;
}

handleInput = (event) => {
    var input = $('#input').value.toUpperCase();

    input = input.replace(/^ +| +$/g, '');

    if (event.keyCode == 13) {
        if(!input)
            return false;
        if($el = $(`cell[data-word="${input}"]`)) {
            getCell($el, true);
        }
        else {
            $('#answer').innerHTML += cell(input, ALL[input]?'err good':'err');
        }

        $('#input').value = '';
        return false;
    }
};

handleAnnotation = (event) => {
    $$('.annotation-container').forEach(x => x.classList.toggle('hidden'));
}

handleFocus = (event, height) => {
    let vh = window.innerHeight - height;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
};

handleReveal = () => {
    $$('cell.hidden').forEach($el => {
        $el.classList.remove('hidden').add('missed');
    });
};

handleClickCell = (event) => {
    var target = event.target,
        attr = target.attributes['data-word'];
    if(attr && !target.classList.contains('hidden')) {
        showDef(attr.value);
    }
    if(target.classList.contains('err')) {
        target.remove();
    }
    if(target.classList.contains('hidden')) {
        getCell(target, false);
    }
}

showDef = (word) => {
    $('#def').innerText = DEFS[word] || 'No definition';
    $('#def').style.display = 'block';
}

if( location.hash ) {
    let hash = decodeURIComponent(location.hash.replace(/^#/, '')),
        match = hash.match(/([UR]),(.*)/);
    if(match) {
        $('#checkRegex').checked = match[1] == 'R';
        $('#input').value = match[2];
    }
}
