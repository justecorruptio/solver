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

ALL = {};
DEFS = {};
POS = {};
RANKS = {};

fetchFile = async (fn, regex, callback) => (
    (await (await fetch(fn)).text()).match(regex).forEach(callback)
);

loadHash = window.onhashchange = () => {
    let locHash = decodeURIComponent(location.hash),
        [_, type, input] = locHash.match(/#([UR]),(.*)/) || [];

    if(!type) return;
    $('#checkRegex').checked = type == 'R';
    $('#input').value = input;
    handleFind();
};

Promise.all([
    fetchFile('nwl2023.txt', /\w+/g, word => ALL[word.upper()] = true),
    fetchFile('def.txt', /[^\n]+\n/g, line => {
        let [_, words, def, pos] = line.match(/(.+)\t([ A-Z]+([a-z]+).+)/);
        words.upper().split(' ').forEach(word => {
            (DEFS[word] = DEFS[word] || []).push(def);
            (POS[word] = POS[word] || {})[pos] = 1;
        });
    }),
    fetchFile('ranks.txt', /[^\n]+\n/g, line => {
        let [hx, rank] = line.split('\t');
        RANKS[hx] = rank | 0;
    }),
]).then(() => {
    $('#input').disabled = false;
}).then(loadHash);

hash = (word) => word.sort().join('');
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

cell = (str, cls, word) => `<cell
    class="${cls || ''}"
    ${word?`data-word="${word}" data-hash="${hash(word)}"`:''}
    onclick="handleClickCell(event)"
>${str}</cell>`;

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
    var input = $('#input').value = $('#input').value.trim().upper();
    if (!input) return;

    var isRegexMode = $('#checkRegex').checked,
        [regex, ...clauses] = input.match(/([^ :]+)/g),
        wrappedRegex = `^(?:${ regex.replace(/@/g, '(.+)') })$`,
        classes = type? `hidden ${type}`: '',
        sortKey = type == 'alpha' ? hash: x => x;

    var res = ALL.keys().map(
        isRegexMode? word => word.match(wrappedRegex): ulu(regex)
    ).filter(matches => matches && (
        clauses.every(clause => {
            var [_, op, len] = clause.match(/^([<>=])(\d+)$/) || [];
            if (op) return eval(`matches[0].length ${op}= ${len}`);
            if (clause.match(/^[?\-+]/)) return true;
            return ALL[clause.replace(/\d/g, x => matches[x | 0])];
        })
    )).map(x => x[0]);

    clauses.forEach(clause => {
        var [_, op, arg] = clause.match(/^([?\-+])(\d+)$/) || []
            rankOp = op == '-'? '<': '>';
        if (op == '?') {
            res.sort(() => Math.random() > .5);
            res = res.slice(0, arg | 0);
        } else {
            eval(`res = res.filter(word => getRank(word) ${rankOp}= (arg | 0))`);
        }
    })

    res.sort((a, b) => a.zlength() + sortKey(a) > b.zlength() + sortKey(b));

    var output = res.map(word => cell(
        annotate(word), type && `hidden ${type}`, word
    )).join('');

    $("#count").innerHTML = res.length;
    $('#answer').innerHTML = output || cell('No solution!');
    $('#input').focus();
    location.hash = `${isRegexMode?'R':'U'},${input.replace(/ /g, ':')}`;
};

getCell = ($el, success) => {
    $$('.last-got').forEach(x=>x.classList.remove('last-got'));
    $el.classList.remove('hidden').add(success?'got':'missed').add('last-got');
    $("#count").innerHTML = $$('cell.hidden').length;
}

handleInput = (event) => {
    var input = $('#input').value.upper().replace(/^ +| +$/g, '');
    if (input && event.keyCode == 13) {
        if ($el = $(`cell[data-word="${input}"]`)) getCell($el, true);
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
    $('#def').innerText = (DEFS[word] || []).join('\n') || 'No definition';
    $('#def').style.display = 'block';
}
