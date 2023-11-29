// Script necessary for every page

// Do not hardcode request URL in js file.
// A example for API: /scores/basic_info/by_class/<int:class_id>/exam/<int:exam_id>
// url = `${protocolPrefix}${host}/api/scores/basic_info/by_class/${class_id}/exam/${exam_id}`;
// fetch(url).then(() => {...});
const protocolPrefix = window.location.protocol + "//";
const host = window.location.host;

const subjectIdToName = {
    1: "语文",
    2: "数学",
    3: "外语",
    4: "物理",
    5: "化学",
    6: "生物",
    7: "政治",
    8: "历史",
    9: "地理",
    255: "总分"
};

// 顶端导航栏和底部页脚的加载
let navbarHtml = null;
let footerHtml = null;

// 避免重复加载导航栏和页脚
$(function () {
    if (navbarHtml === null) {
        $.get("navbar.html", function (response) {
            navbarHtml = response;
            $("#navbar").html(navbarHtml);
            bindNavbarButton();
        });
    } else {
        $("#navbar").html(navbarHtml);
        bindNavbarButton();
    }

    if (footerHtml === null) {
        $.get("footer.html", function (response) {
            footerHtml = response;
            $("#footer").html(footerHtml);
        });
    } else {
        $("#footer").html(footerHtml);
    }
});

// 在首次加载页面时设置初始状态
history.replaceState({ url: window.location.pathname }, null, window.location.pathname);

function bindNavbarButton() {
    // 绑定导航栏按钮和 logo 的点击事件
    $('.navbar-button').off('click').click(function (e) {
        e.preventDefault();  // 阻止默认的页面跳转行为

        // 获取要加载的页面的 URL
        var url = $(this).attr('href');
        // 加载页面内容
        loadPageContent(url);

        // 改变地址栏的 URL
        history.pushState({ url: url }, null, url);
    });

    // 监听 popstate 事件
    window.addEventListener('popstate', function (e) {
        if (e.state && e.state.url) {
            // 加载页面内容
            loadPageContent(e.state.url);
        }
    });

    function loadPageContent(url) {
        // 使用 AJAX 加载页面内容
        $.get(url, function (data) {
            // 将 data 转换为 jQuery 对象
            var $data = $(jQuery.parseHTML(data, document, true));

            // 从加载的内容中提取 .main-content 的内容
            var mainContent = $data.filter('.main-content').add($data.find('.main-content')).html();

            // 检查提取的内容是否为空
            if (mainContent) {
                console.log('Content fetched successfully.');
                // 将提取的内容插入到当前页面的 .main-content 元素中
                $('.main-content').html(mainContent);
            } else {
                console.log('Failed to fetch content.');
            }

            // 更新页面标题
            var title = $data.filter('title').text();
            $('head title').text(title);

            // 加载新的脚本
            $data.filter('script').add($data.find('script')).each(function () {
                var scriptSrc = this.src;

                // 如果脚本没有被加载过，则加载脚本
                var isScriptLoaded = Array.prototype.some.call(document.scripts, function (script) {
                    return script.src === scriptSrc;
                });
                console.log(`Script src: ${scriptSrc}, ${isScriptLoaded ? 'loaded' : 'not loaded'}`);
                if (!isScriptLoaded) {
                    var script = document.createElement('script');
                    if (scriptSrc) {
                        script.src = scriptSrc;
                        console.log('Loading new script: ' + scriptSrc);  // 输出新加载的脚本的 src 属性

                        // 如果是加载 person.js，设置一个全局标记
                        if (scriptSrc.endsWith('person.js')) {
                            window.isPersonJsLoadedFirstTime = true;
                        }
                    } else {
                        script.text = this.innerText;
                    }
                    document.head.appendChild(script);
                } else if (scriptSrc.endsWith('person.js')) {
                    // 如果 person.js 已经被加载过，设置全局标记
                    window.isPersonJsLoadedFirstTime = false;
                }
            });

            // 如果加载的是 person.html，且 person.js 不是第一次被加载，则调用实例
            if (url === 'person.html' && !window.isPersonJsLoadedFirstTime) {
                console.log('Person.js already loaded, initializing PersonPage instance.');
                window["personPage"] = new PersonPage();
                window.personPage.initEventListeners();
            }
        });
    }
}