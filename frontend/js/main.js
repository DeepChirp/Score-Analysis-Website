// 顶端导航栏
$(function () {
    $("#navbar").load("navbar.html", function () {
        // 绑定导航栏按钮和 logo 的点击事件
        $('.navbar-button').off('click').click(function (e) {
            e.preventDefault();  // 阻止默认的页面跳转行为

            // 获取要加载的页面的 URL
            var url = $(this).attr('href');

            // 使用 AJAX 加载页面内容
            $.get(url, function (data) {
                // 将 data 转换为 jQuery 对象
                var $data = $(jQuery.parseHTML(data));

                // 从加载的内容中提取 .main-content 的内容
                var mainContent = $data.filter('.main-content').add($data.find('.main-content')).html();

                // 检查提取的内容是否为空
                if (mainContent) {
                    console.log('Fetch content successful');
                } else {
                    console.log('Fetch content failed');
                }

                // 将提取的内容插入到当前页面的 .main-content 元素中
                $('.main-content').html(mainContent);

                // 更新页面标题
                var title = $data.filter('title').text();
                $('head title').text(title);
            });

            // 改变地址栏的 URL
            history.pushState(null, null, url);
        });
    });
});