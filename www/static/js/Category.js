function Category(categorys, navdom, selectdom) {

    this.navdom = navdom;
    this.selectdom = selectdom;
    this.categorys = categorys;
    this.selectItem = new Object();
    this.selectItem.itemlist = categorys;

    this.shownav = function (dom) {
        dom.empty();
        var temitem = this.selectItem;
        while (temitem) {
            if (!temitem.id) temitem.id = 0;
            if (!temitem.icon) temitem.icon = "";
            if (!temitem.name) temitem.name = "全部";

            var li = document.createElement("li");

            var a = document.createElement("a");
            a.setAttribute("class", 'item-li');
            a.setAttribute("data-id", temitem.id);
            li.appendChild(a);

            var i = document.createElement("i");
            i.setAttribute("class", temitem.icon);
            a.appendChild(i);

            a.innerHTML = temitem.name;
            dom.append(li);
            temitem = temitem.selectitem;
        }
    }


    this.showlist = function (dom) {
        var temlist = this.selectItem;
        while (temlist.selectitem) {
            temlist = temlist.selectitem;
        }
        dom.empty();
        if (temlist.itemlist == null) return;
        for (temitem of temlist.itemlist) {
            var li = document.createElement("li");

            var a = document.createElement("a");
            a.setAttribute("class", 'item-li');
            a.setAttribute("data-id", temitem.id);
            li.appendChild(a);

            var i = document.createElement("i");
            i.setAttribute("class", temitem.icon);
            a.appendChild(i);

            a.innerHTML = temitem.name;
            dom.append(li);

        }
    }


    this.getItembyid = function(list, id) {
        var returnitem = null;

        for (var key in list) {
            item = list[key];
            if (item.id == id) {
                returnitem = item;
                break;
            }
            else {
                if (typeof(item.itemlist) == 'object') {
                    returnitem = arguments.callee(item.itemlist, id);
                    if (returnitem) break;
                }
            }
        }
        return returnitem;
    }

    this.deleteSelectItem = function() {
        var temCategory = this.selectItem;
        while (temCategory != null) {
            var temitem = temCategory;
            temCategory = temCategory.selectitem;
            delete temitem.selectitem;
        }
    }

     this.reloadSelectItembyid = function(id) {
        var temcategory = this.getItembyid(this.categorys, id);

        if (temcategory) {

            while (temcategory.fatherid != 0) {
                var fatheritem = this.getItembyid(this.categorys, temcategory.fatherid);
                if(fatheritem){
                    fatheritem.selectitem = temcategory;
                    temcategory = fatheritem;
                }else {
                    break;
                }

            }
        }

        this.selectItem.selectitem = temcategory;
    }
    function callback(id) {
        var temcategory = getItembyid(this.categorys, id);
        func(temcategory);
    }

    this.shownav(navdom);
    this.showlist(selectdom);

}