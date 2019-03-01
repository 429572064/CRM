import copy

class Pagination(object):

    def __init__(self,current_page_num,all_count,request,per_page_num=10,paper_count=11):
        """
              封装分页相关数据
              :param current_page_num: 当前访问页的数字
              :param all_count:    分页数据中的数据总条数
              :param per_page_num: 每页显示的数据条数
              :param pager_count:  最多显示的页码个数
        """
        try:
            current_page_num = int(current_page_num)
        except Exception as e:
            current_page_num = 1

        if current_page_num < 1:
            current_page_num = 1

        self.current_page_num = current_page_num
        self.all_count = all_count
        self.per_page_num = per_page_num

        self.paper_count = paper_count


        # 实际总页码
        all_paper, tmp = divmod(all_count,per_page_num)
        if tmp:
            all_paper += 1
        self.all_paper = all_paper
        self.paper_count_half = int((paper_count - 1) / 2)
        self.params = copy.deepcopy(request.GET)

    @property
    def start(self):
        return (self.current_page_num - 1) * self.per_page_num
    @property
    def end(self):
        return  self.current_page_num * self.per_page_num

    def page_html(self):
        # 总页码小于等于最大显示页码数
        if self.all_paper <= self.paper_count:
            paper_start = 1
            paper_end = self.all_paper + 1
        # 总页码大于最大显示页码数
        else:
            # 页码在最前
            if self.current_page_num <= self.paper_count_half + 1:
                paper_start = 1
                paper_end = self.paper_count + 1
            else:
                # 页码翻到最后
                if self.current_page_num > self.all_paper - self.paper_count_half:
                    paper_start = self.all_paper - self.paper_count + 1
                    paper_end = self.all_paper + 1

                # 页码在中间
                else:
                    paper_start = self.current_page_num - self.paper_count_half
                    paper_end = self.current_page_num + self.paper_count_half + 1

        # 创建翻页组件 标签
        page_html_list = []

        first_page = '<div class="pull-right"><div style= "margin-right: 30px;" class="dataTables_paginate paging_simple_numbers" id="example1_paginate"><ul class="pagination"><li class="paginate_button page-item"><a aria-controls="example1" tabindex="0" class="page-link" href="?page=%s">首页</a></li>' % (1,)
        page_html_list.append(first_page)
        if self.current_page_num <= 1:
            prev_page='<li class="paginate_button page-item previous disabled" id="example1_previous"><a aria-controls="example1" tabindex="0" class="page-link" href="#">上一页</a></li>'
        else:
            prev_page = '<li class="paginate_button page-item previous" id="example1_previous"><a aria-controls="example1" tabindex="0" class="page-link" href="?page=%s">上一页</a></li>' % (self.current_page_num - 1 ,)
        page_html_list.append(prev_page)

        for i in range(paper_start,paper_end):
            self.params["page"] = i
            if i == self.current_page_num:
                temp = '<li class="paginate_button page-item active"><a aria-controls="example1" data-dt-idx="1"tabindex="0" class="page-link" href="?%s">%s</a></li>' % (self.params.urlencode(),i)
            else:
                temp = '<li class="paginate_button page-item"><a aria-controls="example1" data-dt-idx="1"tabindex="0" class="page-link" href="?%s">%s</a></li>' % (self.params.urlencode(), i)
            page_html_list.append(temp)

        if self.current_page_num >= self.all_paper:
            next_page = '<li class="paginate_button page-item next disabled"><a aria-controls="example1" tabindex="0" class="page-link" herf="#">下一页</a></li>'
        else:
            next_page = '<li class="paginate_button page-item next" id="example1_next"><a aria-controls="example1" tabindex="0" class="page-link" href="?page=%s">下一页</a></li>' % (self.current_page_num+1)
        page_html_list.append(next_page)

        last_page ='<li class="paginate_button page-item"><a aria-controls="example1" tabindex="0" class="page-link" href="?page=%s">尾页</a></ul></div></div></div>' % (self.all_paper,)
        page_html_list.append(last_page)
        return ''.join(page_html_list)

