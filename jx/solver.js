Object.prototype.keys = function(){return Object.keys(this)};
String.prototype.sort = function(){return [...this].sort().join('')};
String.prototype.upper = function(){return this.toUpperCase()};
$ = x => document.querySelector(x);
$$ = x => document.querySelectorAll(x);
LETTERS = [...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'];
ALL = {}; GRAMS = {}; DEFS = {}; POS = {}; RANKS = {};

fetchFile = async (fn, cb) => (await (await fetch(fn)).text()).match(/[^\n]+/g).forEach(cb);

Promise.all([
    fetchFile('nwl2023.txt', word => {
        word = word.upper();
        ALL[word] = true;
        (GRAMS[word.sort()] ||= []).push(word);
    }),
    fetchFile('def.txt', line => {
        let [, words, def, pos] = line.match(/(.+)\t([ A-Z]+([a-z]+).+)/);
        words.upper().split(' ').forEach(word => {
            (DEFS[word] ||= []).push(def);
            (POS[word] ||= {})[pos] = 1;
        });
    }),
    fetchFile('ranks.txt', line => {
        let [hash, rank] = line.split('\t');
        RANKS[hash] = rank | 0;
    }),
]).then(() => {$('#input').disabled = false})

ulu = (pattern) => {
    let any = /@/.test(pattern),
        letters = pattern.replace(/[?@]/g, '').sort(),
        regex = RegExp(['^', ...letters, '$'].join('.*'));
    return (word) => (any || pattern.length == word.length) && word.sort().match(regex);
}

sm = (cls, text) => `<small class="annotation ${cls}">${text}</small>`;

cell = (str, cls, word) => `<cell class="${cls || ''}"
    ${word ? `data-word="${word}" data-hash="${word.sort()}"` : ''}
    onclick="handleClickCell(event)">${str}</cell>`;

annotate = (word) => {
    let hidden = $('#checkAnnotate').checked ? '' : 'hidden',
        pre = LETTERS.filter(l => ALL[l + word]).join(''),
        post = LETTERS.filter(l => ALL[word + l]).join(''),
        rank = (RANKS[word.sort()] || 99999) / 20000;
    return `<div class="annotation-container ${hidden}">
        ${sm('left', pre + (ALL[word.substring(1)] ? '●' : ''))}
        ${sm('super left', '★'.repeat(rank))} ${word}
        ${sm('right', (ALL[word.slice(0,-1)] ? '●' : '') + post)}
        ${sm('super right', (POS[word] || {}).keys().join('&nbsp;'))}
    </div>`;
}

handleFind = (type) => {
    var input = $('#input').value = $('#input').value.trim().upper();
    if (!input) return;
    var isRegexMode = $('#checkRegex').checked,
        [regex, ...clauses] = input.match(/([^ :]+)/g),
        wrappedRegex = `^(?:${regex.replace(/@/g,'(.+)')})$`,
        sortKey = type == 'alpha' ? w => w.sort() : w => w;
    var res = ALL.keys().map(
        isRegexMode ? word => word.match(wrappedRegex) : ulu(regex)
    ).filter(matches => matches && clauses.every(clause => {
        var [, op, len] = clause.match(/^([<>=])(\d+)$/) || [];
        return op ? eval(`matches[0].length ${op}= ${len}`)
            : /^[?\-+]/.test(clause) || ALL[clause.replace(/\d/g, x => matches[x|0])];
    })).map(x => x[0]);
    clauses.forEach(clause => {
        var [, arg] = clause.match(/^\?(\d+)$/) || [];
        if (!arg) return;
        res = res.sort(() => Math.random() - .5) .slice(0, arg | 0);
        if (!isRegexMode) res = [...new Set(res.flatMap(w => GRAMS[w.sort()]))];
    });
    res.sort((a, b) => a.length - b.length || (sortKey(a) > sortKey(b) ? 1 : -1));
    $("#count").innerHTML = res.length;
    $('#answer').innerHTML = res.map(
        word => cell(annotate(word), type && `hidden ${type}`, word)
    ).join('') || cell('No solution!');
    $('#input').focus();
};

getCell = (el, success) => {
    $$('.last-got').forEach(x => x.classList.remove('last-got'));
    el.classList.replace('hidden', success ? 'got' : 'missed');
    el.classList.add('last-got');
    $("#count").innerHTML = $$('cell.hidden').length;
}

handleInput = ({keyCode, shiftKey}) => {
    var input = $('#input').value.upper().trim();
    if (input && keyCode == 13) {
        if (shiftKey) return handleFind();
        var el = $(`cell[data-word="${input}"]`);
        if (el) getCell(el, true);
        else $('#answer').innerHTML += cell(input, ALL[input]?'err good':'err');
        $('#input').value = '';
    }
};

handleAnnotation = () => $$('.annotation-container').forEach(x => x.classList.toggle('hidden'));
handleReveal = () => $$('cell.hidden').forEach(x => x.classList.replace('hidden', 'missed'));

handleClickCell = ({target, target: {dataset: {word}}}) => {
    if (target.matches('.err')) return target.remove();
    if (target.matches('.hidden')) return getCell(target, false);
    if (word) {
        $('#def').innerText = (DEFS[word]||[]).join('\n') || 'No definition';
        $('#def').style.display = 'block';
    }
}

visualViewport.addEventListener('resize', (event) => {
    document.documentElement.style.setProperty('--vh', `${event.target.height}px`);
});
