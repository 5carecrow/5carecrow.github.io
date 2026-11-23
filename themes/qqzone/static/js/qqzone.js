(function () {
  var searchInput = document.getElementById('qq-search');
  var searchBox = document.getElementById('qq-search-results');

  if (searchInput && searchBox) {
    var posts = [];

    function render(query) {
      var q = (query || '').trim().toLowerCase();
      searchBox.innerHTML = '';

      if (!q) {
        var tip = document.createElement('p');
        tip.className = 'empty';
        tip.textContent = '输入关键词开始搜索';
        searchBox.appendChild(tip);
        return;
      }

      var matches = posts.filter(function (post) {
        var haystack = [post.title, post.summary, (post.tags || []).join(' ')].join(' ').toLowerCase();
        return haystack.indexOf(q) !== -1;
      });

      if (!matches.length) {
        var none = document.createElement('p');
        none.className = 'empty';
        none.textContent = '没有找到相关日志';
        searchBox.appendChild(none);
        return;
      }

      matches.forEach(function (post) {
        var item = document.createElement('div');
        item.className = 'search-result';

        var link = document.createElement('a');
        link.href = post.url;
        link.textContent = post.title;

        var meta = document.createElement('p');
        meta.textContent = post.date + ' · ' + (post.summary || '');

        item.appendChild(link);
        item.appendChild(meta);
        searchBox.appendChild(item);
      });
    }

    fetch('/search/index.json')
      .then(function (response) {
        if (!response.ok) throw new Error('index unavailable');
        return response.json();
      })
      .then(function (data) {
        posts = Array.isArray(data) ? data : [];
        render(searchInput.value);
      })
      .catch(function () {
        searchBox.innerHTML = '';
        var err = document.createElement('p');
        err.className = 'empty';
        err.textContent = '搜索索引加载失败，请稍后刷新重试';
        searchBox.appendChild(err);
      });

    searchInput.addEventListener('input', function () {
      render(searchInput.value);
    });
  }

  var form = document.getElementById('qq-guestbook-form');
  var list = document.getElementById('qq-guestbook-list');
  var key = 'qqzone-guestbook';

  function loadMessages() {
    try {
      return JSON.parse(localStorage.getItem(key) || '[]');
    } catch (e) {
      return [];
    }
  }

  function saveMessages(messages) {
    localStorage.setItem(key, JSON.stringify(messages));
  }

  function renderMessages() {
    if (!list) return;
    list.innerHTML = '';
    var messages = loadMessages();

    if (!messages.length) {
      var empty = document.createElement('p');
      empty.className = 'empty';
      empty.textContent = '还没有留言，来抢个沙发吧。';
      list.appendChild(empty);
      return;
    }

    messages.slice().reverse().forEach(function (message) {
      var item = document.createElement('div');
      item.className = 'gb-item';

      var title = document.createElement('strong');
      title.textContent = message.name;

      var time = document.createElement('time');
      time.textContent = message.time;

      var text = document.createElement('p');
      text.textContent = message.text;

      item.appendChild(title);
      item.appendChild(time);
      item.appendChild(text);
      list.appendChild(item);
    });
  }

  if (form && list) {
    renderMessages();

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var name = document.getElementById('gb-name').value.trim();
      var text = document.getElementById('gb-text').value.trim();
      if (!name || !text) return;

      var messages = loadMessages();
      messages.push({
        name: name,
        text: text,
        time: new Date().toLocaleString('zh-CN', { hour12: false })
      });
      saveMessages(messages);
      form.reset();
      renderMessages();
    });
  }
})();
