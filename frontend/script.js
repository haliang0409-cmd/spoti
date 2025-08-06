$(document).ready(function() {
    const table = $('#pricesTable').DataTable({
        "language": {
            "search": "搜索:",
            "lengthMenu": "每页显示 _MENU_ 条记录",
            "info": "显示第 _START_ 到 _END_ 条，共 _TOTAL_ 条记录",
            "infoEmpty": "没有可用数据",
            "infoFiltered": "(从 _MAX_ 条总记录中过滤)",
            "paginate": { "first": "首页", "last": "末页", "next": "下一页", "previous": "上一页" },
            "loadingRecords": "加载中...",
            "zeroRecords": "未找到匹配的记录",
            "emptyTable": "数据加载中或定时任务尚未运行..."
        }
    });

    // 使用 cache-busting 参数确保获取最新文件
    fetch(`spotify_prices.json?v=${new Date().getTime()}`)
      .then(response => {
            if (!response.ok) {
                throw new Error('网络响应错误或 spotify_prices.json 文件未找到。');
            }
            const lastModified = response.headers.get('Last-Modified');
            $('#last-updated').text(lastModified? new Date(lastModified).toLocaleString() : new Date().toLocaleString());
            return response.json();
        })
      .then(data => {
            if (data && data.length > 0) {
                table.clear();
                data.forEach(item => {
                    table.row.add([
                        item.country_code,
                        item.plan_name,
                        `${item.local_price.toFixed(2)} ${item.local_currency}`,
                        item.price_cny? `¥${item.price_cny.toFixed(2)}` : 'N/A'
                    ]).draw(false);
                });
            } else {
                 $('#pricesTable tbody').html('<tr><td colspan="4">未能加载价格数据。可能是每日抓取任务尚未运行或失败。</td></tr>');
            }
        })
      .catch(error => {
            console.error('获取价格数据时出错:', error);
            $('#pricesTable tbody').html('<tr><td colspan="4">加载数据失败。请检查浏览器控制台获取更多信息。</td></tr>');
            $('#last-updated').text('失败');
        });
});
