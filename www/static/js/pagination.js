function Pagination(maxpage,pages, selectPage, dom) {

    this.__maxpage = parseInt(maxpage);
    this.__pages = parseInt(pages);
    this.__selectPage = parseInt(selectPage);
    this.__dom = dom;
    this.__offset = 0;
    this.getselectPage = function () {
        return this.__selectPage;
    }
    this.selectPage = function (selectPage) {
        this.__offset = 0;
        this.__selectPage = parseInt(selectPage);
        this.show(this.__dom);
    };

    this.offset = function (offset) {
        this.__selectPage = this.__selectPage+offset;
        this.show(this.__dom);
    }


    this.show = function(dom){
        this.__dom = dom;
        this.__dom.empty();
        begin = 1;
        end = pages;
        middle = this.__selectPage;

        begin = middle-parseInt(this.__maxpage/2) + this.__maxpage%2;
        if(begin<=1){
            begin = 1;
        }
        end = begin+this.__maxpage;
        if(end>pages){
            end = pages;
            begin = end-this.__maxpage;
            if(begin<=1){
                begin = 1;
            }
        }
        if(begin > 1){
            li = document.createElement("li");
            li_a = document.createElement("a");
            li.appendChild(li_a);
            li_a.innerHTML = "«";
            dom.append(li);
            begin = begin+1;
        }
        for(i = begin; i<end; i++){
            li = document.createElement("li");
            li_a = document.createElement("a");
            li.appendChild(li_a);
            li_a.innerHTML = i;
            dom.append(li);
            if(i == this.__selectPage){
                li_a.setAttribute("style","color: #f77b6f;");
            }
            dom.append(li);

        }
        if(end < pages){

            li = document.createElement("li");
            li_a = document.createElement("a");
            li.appendChild(li_a);
            li_a.innerHTML = "»";
            dom.append(li);
        }else {
            li = document.createElement("li");
            li_a = document.createElement("a");
            li.appendChild(li_a);
            li_a.innerHTML = end;
            dom.append(li);
            if(i == this.__selectPage){
                li_a.setAttribute("style","color: #f77b6f;");

            }
            dom.append(li);
        }

    }
    this.show(dom);
}