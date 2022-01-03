$(function () {

    $('#add_btn').click(function () {
        methods.addHandle()
    })

    $('#show_tbody').on('click','.edit', function () {
        trIndex = $('.edit', '#show_tbody').index($(this));
        addEnter = false;
        $(this).parents('tr').addClass('has_case');
        methods.editHandle(trIndex);
    })

    $('#search_btn').click(function () {
        methods.seachName();
    })

    $('#back_btn').click(function () {
        $('#Ktext').val('');
        methods.resectList();
    })

     $('#show_tbody').on('click','.del', function () {
        trIndex = $('.del', '#show_tbody').index($(this));
        var tar = $('#show_tbody tr').eq(trIndex);
        cur_id = parseInt(tar.children('td').eq(0).html());
        var self = this;
        $.ajax({
                type: "post",
                url: "./delrules",
                data: {cur_id: cur_id},
                dataType: "json",
                success:function (datas){
                    if(datas.success){
                        $(self).parents('tr').remove();
                        //$(this).parents('tr').remove();
                        /*if(addEnter){
                            //alert(addEnter);
                            cur_id = datas.id;
                            tdStr = '<td>' + cur_id + '</td>' + tdStr;
                            $('#show_tbody').append('<tr>' + tdStr + '</tr>');
                            $('#renyuan').modal('hide');
                        }else{
                            //alert(addEnter);
                            tdStr = '<td>' + cur_id + '</td>' + tdStr;
                            $('#show_tbody tr').eq(trIndex).empty().append(tdStr);
                            addEnter = true;
                            cur_id = 0;
                            $('#renyuan').modal('hide');
                        }*/

                    }
                }
            })

    })

    $('#renyuan').on('hide.bs.modal',function() {
        addEnter = true;
        $('#show_tbody tr').removeClass('has_case');
        $('#xztb input').val('');
        $('#xztb select').find('option:first').prop('selected', true)
    });

})

var addEnter = true,
    noRepeat = true,
    jobArr = [],
    phoneArr = [],
    tdStr = '',
    trIndex,
    hasNullMes = false,
    tarInp = $('#xztb input'),
    tarSel = $('#xztb select'),
    modify = true,
    cur_id = 0,
    exp = "",
    des = "",
    is_com = 0,
    is_en = 1,
    pos = {};

var methods = {

    addHandle: function (the_index) {
        hasNullMes = false;
        //alert(addEnter);
        methods.checkMustMes();
        /*if (hasNullMes) {
            return;
        }*/

            //methods.checkRepeat();

        if (noRepeat) {

            methods.setStr();

            $.ajax({
                type: "post",
                url: "./addrules",
                data: pos,
                dataType: "json",
                success:function (datas){
                    if(datas.success){
                        if(addEnter){
                            //alert(addEnter);
                            cur_id = datas.id;
                            tdStr = '<td>' + cur_id + '</td>' + tdStr;
                            $('#show_tbody').append('<tr>' + tdStr + '</tr>');
                            $('#renyuan').modal('hide');
                        }else{
                            //alert(addEnter);
                            tdStr = '<td>' + cur_id + '</td>' + tdStr;
                            $('#show_tbody tr').eq(trIndex).empty().append(tdStr);
                            addEnter = true;
                            cur_id = 0;
                            $('#renyuan').modal('hide');
                        }

                    }else{
                        alert('规则语法有问题');
                        $('#renyuan').modal('hide');
                    }
                }
            })

        }


    },
    editHandle: function (the_index) {

        var tar = $('#show_tbody tr').eq(the_index);
        var nowConArr = [];
        cur_id = parseInt(tar.children('td').eq(0).html());
        for (var i=1; i<tar.find('td').length-1;i++) {
            var a = tar.children('td').eq(i).html();
            nowConArr.push(a);

        }

        $('#renyuan').modal('show');

        for (var j=0;j<tarInp.length;j++) {
            tarInp.eq(j).val(nowConArr[j])
        }
        for (var p=0;p<tarSel.length;p++) {
            var the_p = p+tarInp.length;
            tarSel.eq(p).val(nowConArr[the_p]);
        }

    },
    setStr: function () {

        tdStr = '';
        pos = {};
        exp = "";
        des = "";
        is_com = 0;
        is_en = 1;
        //for (var a=0; a<tarInp.length; a++) {
        exp = tarInp.eq(0).val();
        tdStr += '<td>' + exp + '</td>';
        des = tarInp.eq(1).val();
        tdStr += '<td>' + des + '</td>';
        //}
        //for (var b=0; b<tarSel.length; b++) {
        if(tarSel.eq(0).val() == '是'){
            is_com = 1;
        }
        if(tarSel.eq(1).val() == '否'){
            is_en = 0;
        }
        tdStr+= '<td>' + tarSel.eq(0).val() + '</td>';
        tdStr+= '<td>' + tarSel.eq(1).val() + '</td>';
        //}
        tdStr+= '<td><a href="#" class="edit">编辑</a> <a href="#" class="del">删除</a></td>';
        pos = {cur_id:cur_id, exp:exp, description:des, is_combined_data:is_com, is_enabled:is_en};

    },
    seachName: function () {

        var a = $('#show_tbody tr');
        var nameVal = $('#Ktext').val().trim();
        var nameStr = '',
            nameArr = [];

        if (nameVal==='') {
            bootbox.alert({
                title: "来自火星的提示",
                message: "搜索内容不能为空",
                closeButton:false
            })
            return;
        }

        for (var c=0;c<a.length;c++) {
            //var txt = $('td:first', a.eq(c)).html().trim();
            var txt = a.eq(c).children('td').eq(2).html().trim();
            nameArr.push(txt);
        }

        a.hide();
        for (var i=0;i<nameArr.length;i++) {
            if (nameArr[i].indexOf(nameVal)>-1) {
                a.eq(i).show();
            }
        }
    },
    resectList: function () {
        $('#show_tbody tr').show();
    },
    checkMustMes: function () {

        if ($('.exp').val().trim()==='') {
            bootbox.alert({
                title: "来自火星的提示",
                message: "表达式/关键词为必选项，请填写",
                closeButton:false
            })
            hasNullMes = true;
            return
        }
        if ($('.des').val().trim()==='') {
            bootbox.alert({
                title: "来自火星的提示",
                message: "描述为必填项，请填写",
                closeButton:false
            })
            hasNullMes = true;
            return
        }
        /*if ($('.phoneNum').val().trim()==='') {
            bootbox.alert({
                title: "来自火星的提示",
                message: "手机号为必选项，请填写",
                closeButton:false
            })
            hasNullMes = true;
            return
        }*/

    },
    checkRepeat: function () {

        jobArr = [], phoneArr = [];

        for (var i = 0; i<$('#show_tbody tr:not(".has_case")').length;i++) {
            var par = '#show_tbody tr:not(".has_case"):eq(' + i + ')';
            var a = $('td:eq(1)', par).html().trim(),
                b = $('td:eq(2)', par).html().trim();
            jobArr.push(a);
            phoneArr.push(b);
        }
        var jobNum = $('.jobNum').val().trim(),
            phoneNum = $('.phoneNum').val().trim();

        if (jobArr.indexOf(jobNum)>-1) {
            noRepeat = false;
            bootbox.alert({
                title: "来自火星的提示",
                message: "工号重复了，请重新输入",
                closeButton:false
            })
            return;
        }
        if (phoneArr.indexOf(phoneNum)>-1) {
            noRepeat = false;
            bootbox.alert({
                title: "来自火星的提示",
                message: "手机号码重复了，请重新输入",
                closeButton:false
            })
            return;
        }
        noRepeat = true;
    }
}