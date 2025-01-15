Object.prototype.keys = function(){return Object.keys(this)};
String.prototype.sort = function() {return this.split('').sort()};
String.prototype.upper = function() {return this.toUpperCase()};
String.prototype.zlength = function() {return `${this.length}`.padStart(2, '0')};
DOMTokenList.prototype._add = DOMTokenList.prototype.add;
DOMTokenList.prototype.add = function(v) {this._add(v); return this};
DOMTokenList.prototype._remove = DOMTokenList.prototype.remove;
DOMTokenList.prototype.remove = function(v) {this._remove(v); return this};

$ = x => document.querySelector(x);
$$ = x => document.querySelectorAll(x);

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

hash = word => word.sort().join('');

ALL = {};
DEFS = {};
POS = {};
RANKS = {};

fetchFile = async (fn, regex, callback) =>
    (await (await fetch(fn)).text()).match(regex).forEach(callback);

Promise.all([
    fetchFile('nwl2023.txt', /\w+/g, word => ALL[word.upper()] = true),
    fetchFile('def.txt', /[^\n]+\n/g, line => {
        var [_, words, def, pos] = line.match(/(.+)\t([ A-Z]+([a-z]+).+)/);
        words.upper().split(' ').forEach(word => {
            DEFS[word] = def;
            (POS[word] = POS[word] || {})[pos] = 1;
        });
    }),
    fetchFile('ranks.txt', /[^\n]+\n/g, line => {
        var [hx, rank] = line.split('\t');
        RANKS[hx] = rank | 0;
    }),
]).then(() => {
    let locHash = decodeURIComponent(location.hash),
        [_, type, input] = locHash.match(/#([UR]),(.*)/);

    $('#input').disabled = false;
    if(!locHash || !type) return;

    $('#checkRegex').checked = type == 'R';
    $('#input').value = input;
    handleFind();
});


getRank = (word) => (RANKS[hash(word)] || 99999) / 20000;

ulu = (pattern) => {
    var count = 0,
        any = false;

    pattern = pattern.replace(/[?]/g, x=>(count++, ''));
    pattern = pattern.replace(/[@]/g, x=>(any=true, ''));
    pattern = new RegExp(['^', ...pattern.sort(), '$'].join('(.*)'), 'i');

    return (word) => {
        var hx = hash(word),
            result = hx.replace(pattern, (...v)=>v.slice(1,-2).join(''));
        return result != hx && (any || result.length == count)? [word]: null;
    }
}

cell = (str, cls, word, addHash) => ( `<cell
    class="${cls || ''}"
    ${word?`data-word="${word}"`:''}
    ${addHash?`data-hash="${hash(word)}"`:''}
    onclick="handleClickCell(event)"
>${str}</cell>`);

annotate = (word) => {
    var hidden = $('#checkAnnotate').checked ? '': 'hidden',
        rank = '*'.repeat(getRank(word)),
        pos = (POS[word] || {}).keys().join('&nbsp;'),
        pre = LETTERS.filter(l=>ALL[l + word]).join(''),
        post = LETTERS.filter(l=>ALL[word + l]).join(''),
        preDel = ALL[word.substring(1)]? '●': '',
        postDel = ALL[word.substring(0, word.length - 1)]? '●': '';
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
        classes = '',
        match_func;

    input = $('#input').value = $('#input').value.replace(/^\s+|\s+$/g, '');
    input = input.upper();

    if(!input) return;

    var [regex, ...clauses] = input.match(/([^ :]+)/g);

    if ($('#checkRegex').checked) {
        regex = `^(?:${regex.replace(/@/g, '(.+)')})$`;
        match_func = (word) => word.match(regex);
    } else {
        match_func = ulu(regex);
    }

    found = ALL.keys().map(match_func).filter(x=>x);

    res = found.filter(matches => (
        clauses.every(clause => {
            var [_, op, len] = clause.match(/^([<>=])(\d+)$/) || [];
            if(op) return eval(`matches[0].length ${op}= ${len}`);
            if (clause.match(/^[?\-+]/)) return true;
            return ALL[clause.replace(/\d/g, x => matches[x | 0])];
        })
    )).map(x => x[0]);

    clauses.forEach(clause => {
        var arg;
        if (arg = clause.match(/^[?](\d+)$/)) {
            res.sort((a, b) => Math.random() > .5);
            res = res.slice(0, arg[1] | 0);
        }
        if (arg = clause.match(/^[\-](\d+)$/)) {
            res = res.filter(word => getRank(word) <= (arg[1] | 0))
        }
        if (arg = clause.match(/^[+](\d+)$/)) {
            res = res.filter(word => getRank(word) >= (arg[1] | 0))
        }
    })

    res.sort((a, b) => a.zlength() + a > b.zlength() + b);

    if (type == 'blur') {
        classes = 'blur hidden';
    } else if (type == 'alpha') {
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
    var input = $('#input').value.upper().replace(/^ +| +$/g, '');
    if (input && event.keyCode == 13) {
        if($el = $(`cell[data-word="${input}"]`)) getCell($el, true);
        else $('#answer').innerHTML += cell(input, ALL[input]?'err good':'err');

        $('#input').value = '';
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
    $$('cell.hidden').forEach($el => $el.classList.remove('hidden').add('missed'));
};

handleClickCell = (event) => {
    var target = event.target,
        attr = target.attributes['data-word'];
    if(attr && !target.classList.contains('hidden')) showDef(attr.value);
    if(target.classList.contains('err')) target.remove();
    if(target.classList.contains('hidden')) getCell(target, false);
}

showDef = (word) => {
    $('#def').innerText = DEFS[word] || 'No definition';
    $('#def').style.display = 'block';
}
