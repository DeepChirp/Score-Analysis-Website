// Script necessary for every page

// Do not hardcode request URL in js file.
// A example for API: /scores/basic_info/by_class/<int:class_id>/exam/<int:exam_id>
// url = `${protocolPrefix}${host}/api/scores/basic_info/by_class/${class_id}/exam/${exam_id}`;
// fetch(url).then(() => {...});
const protocolPrefix = window.location.protocol + "//";
const host = window.location.host;

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
            var $data = $(jQuery.parseHTML(data));

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
        });
    }
}