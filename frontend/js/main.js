// 顶端导航栏
$(function () {
    $("#navbar").load("navbar.html", function () {
        // 绑定导航栏按钮的点击事件
        $('.navbar-button').click(function (e) {
            e.preventDefault();  // 阻止默认的页面跳转行为

            // 获取要加载的页面的 URL
            var url = $(this).attr('href');

            // 使用 AJAX 加载页面内容
            $.get(url, function (data) {
                // 将加载的内容插入到 .content 元素中
                $('.content').html(data);

                // 更新页面标题
                var title = $(data).filter('title').text();
                $('head title').text(title);
            });

            // 改变地址栏的 URL
            history.pushState(null, null, url);
        });
    });
});