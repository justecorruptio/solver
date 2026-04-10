Object.prototype.keys = function(){return Object.keys(this)};
String.prototype.sort = function(){return [...this].sort()};
String.prototype.upper = function(){return this.toUpperCase()};
String.prototype.zlength = function(){return (this.length+'').padStart(2,'0')};
for (let m of ['add','remove']) {
    let orig = DOMTokenList.prototype[m];
    DOMTokenList.prototype[m] = function(v){orig.call(this,v); return this};
}

$ = x => document.querySelector(x);
$$ = x => document.querySelectorAll(x);
LETTERS = [...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'];
ALL = {}; GRAMS = {}; DEFS = {}; POS = {}; RANKS = {};

fetchFile = async (fn, cb) => (await (await fetch(fn)).text()).match(/[^\n]+/g).forEach(cb);

Promise.all([
    fetchFile('nwl2023.txt', word => {
        word = word.upper();
        let hx = hash(word);
        ALL[word] = true;
        (GRAMS[hx] ||= []).push(word);
    }),
    fetchFile('def.txt', line => {
        let [_, words, def, pos] = line.match(/(.+)\t([ A-Z]+([a-z]+).+)/);
        words.upper().split(' ').forEach(word => {
            (DEFS[word] ||= []).push(def);
            (POS[word] ||= {})[pos] = 1;
        });
    }),
    fetchFile('ranks.txt', line => {
        let [hx, rank] = line.split('\t');
        RANKS[hx] = rank | 0;
    }),
]).then(() => {$('#input').disabled = false;})

hash = word => word.sort().join('');
getRank = word => (RANKS[hash(word)] || 99999) / 20000;

ulu = (pattern) => {
    let any = !!pattern.match(/@/),
        letters = pattern.replace(/[?@]/g, '').sort(),
        regex = new RegExp(['^', ...letters, '$'].join('.*'));
    return (word) => (any || pattern.length == word.length) && hash(word).match(regex);
}

cell = (str, cls, word) => `<cell class="${cls || ''}"
    ${word ? `data-word="${word}" data-hash="${hash(word)}"` : ''}
    onclick="handleClickCell(event)">${str}</cell>`;

annotate = (word) => {
    let hidden = $('#checkAnnotate').checked ? '' : 'hidden',
        rank = '*'.repeat(getRank(word)),
        pos = (POS[word] || {}).keys().join('&nbsp;'),
        pre = LETTERS.filter(l => ALL[l + word]).join(''),
        post = LETTERS.filter(l => ALL[word + l]).join(''),
        preDel = ALL[word.substring(1)] ? '●' : '',
        postDel = ALL[word.slice(0, -1)] ? '●' : '';
    return `<div class="annotation-container ${hidden}">
        <small class="annotation left">${pre}${preDel}</small>
        <small class="annotation rank">${rank}</small>${word}
        <small class="annotation right">${postDel}${post}</small>
        <small class="annotation pos">${pos}</small></div>`;
}

handleFind = (type) => {
    var input = $('#input').value = $('#input').value.trim().upper();
    if (!input) return;

    var isRegexMode = $('#checkRegex').checked,
        [regex, ...clauses] = input.match(/([^ :]+)/g),
        wrappedRegex = `^(?:${ regex.replace(/@/g, '(.+)') })$`,
        sortKey = type == 'alpha' ? hash : x => x;

    var res = ALL.keys().map(
        isRegexMode ? word => word.match(wrappedRegex) : ulu(regex)
    ).filter(matches => matches && clauses.every(clause => {
        var [_, op, len] = clause.match(/^([<>=])(\d+)$/) || [];
        if (op) return eval(`matches[0].length ${op}= ${len}`);
        if (clause.match(/^[?\-+]/)) return true;
        return ALL[clause.replace(/\d/g, x => matches[x | 0])];
    })).map(x => x[0]);

    clauses.forEach(clause => {
        var [_, op, arg] = clause.match(/^([?\-+])(\d+)$/) || []
            rankOp = op == '-'? '<': '>';
        if (op == '?') {
            res.sort(() => Math.random() - .5);
            res = res.slice(0, arg | 0);
            if (!isRegexMode) {
                res = [...new Set(res.map(w => GRAMS[hash(w)]).flat())];
            }
        } else {
            eval(`res = res.filter(word => getRank(word) ${rankOp}= (arg | 0))`);
        }
    })

    res.sort((a, b) => a.zlength() + sortKey(a) > b.zlength() + sortKey(b));

    var output = res.map(w => cell(annotate(w), type && `hidden ${type}`, w)).join('');
    $("#count").innerHTML = res.length;
    $('#answer').innerHTML = output || cell('No solution!');
    $('#input').focus();
};

getCell = ($el, success) => {
    $$('.last-got').forEach(x=>x.classList.remove('last-got'));
    $el.classList.remove('hidden').add(success?'got':'missed').add('last-got');
    $("#count").innerHTML = $$('cell.hidden').length;
}

handleInput = (event) => {
    var input = $('#input').value.upper().trim();
    if (input && event.keyCode == 13) {
        if (event.shiftKey) { handleFind(); return; }
        if ($el = $(`cell[data-word="${input}"]`)) getCell($el, true);
        else $('#answer').innerHTML += cell(input, ALL[input]?'err good':'err');
        $('#input').value = '';
    }
};

handleAnnotation = () => $$('.annotation-container').forEach(x => x.classList.toggle('hidden'));

handleReveal = () => $$('cell.hidden').forEach(x => x.classList.remove('hidden').add('missed'));

handleClickCell = (event) => {
    var target = event.target, word = target.dataset.word;
    if(word && !target.classList.contains('hidden')) showDef(word);
    if(target.classList.contains('err')) target.remove();
    if(target.classList.contains('hidden')) getCell(target, false);
}

showDef = (word) => {
    $('#def').innerText = (DEFS[word] || []).join('\n') || 'No definition';
    $('#def').style.display = 'block';
}

window.visualViewport.addEventListener('resize', (event) => {
    document.documentElement.style.setProperty('--vh', `${event.target.height}px`);
});
