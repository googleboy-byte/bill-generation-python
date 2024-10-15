var current_billno = null;
var current_roomnums = [];
var current_kotnums = [];
var allitemslist = []
var showingitemslist = []
var current_customername = "";
let newbill = new Map();
var itemcount = 1
// var temptotal = 0
var discount_percent = 0;
var delivery_charges = 0;
var sumtotal = 0;

document.addEventListener('DOMContentLoaded', function() {
    // alert("page loaded");
    const roomnums_inputField = document.getElementById('room_nums_input');
    const kotnums_inputField = document.getElementById('kot_nums_input');
    const menusearch_input_div = document.getElementById('menusearch_input');
    const discountpercinp = document.getElementById("discount_percent_input");
    const deliverychargeinp = document.getElementById("delivery_charge_input");
    const custname_input_div = document.getElementById("cust_name_input");
    const searchbillsinput = document.getElementById("searchbills");
    const searchbillsdatecb = document.getElementById("datecbox_filter");
    const searchbillscnamecb = document.getElementById("cnamecbox_filter");
    const searchbillskotcb = document.getElementById("kotcbox_filter");

    roomnums_inputField.addEventListener('input', function() {
            if (roomnums_inputField.value.trim().includes(",")) {
                var room_num_inp = roomnums_inputField.value;
                // alert(roomnums_inputField.value);
                var beforeComma = room_num_inp.split(',')[0];
                // alert(beforeComma);
                roomnums_inputField.value = "";
                if (!current_roomnums.includes(beforeComma)) {
                    current_roomnums.push(beforeComma);
                    update_Rooms_fend();
                }
            }
    });

    kotnums_inputField.addEventListener('input', function() {
        if (kotnums_inputField.value.trim().includes(",")) {
            var kot_num_inp = kotnums_inputField.value;
            // alert(roomnums_inputField.value);
            var beforeComma_kot = kot_num_inp.split(',')[0];
            // alert(beforeComma);
            kotnums_inputField.value = "";
            if (!current_kotnums.includes(beforeComma_kot)) {
                current_kotnums.push(beforeComma_kot);
                update_Kots_fend();
            }
        }
    });

    menusearch_input_div.addEventListener('input', function() {
        var menusearchcrit = menusearch_input_div.value;
        if (menusearchcrit.trim() == "") {
            loadItemsListFend();
        } else{
            menusearchBendFend(menusearchcrit);
        }
    });

    custname_input_div.addEventListener('input', function() {
        current_customername = custname_input_div.value;
    });

    discountpercinp.addEventListener('input', function() {
        // if(discountpercinp.value != ""){
        updateSumTotalFendBend(setfocusid="discount_percent_input");
        // }
    });

    deliverychargeinp.addEventListener('input', function() {
        // if(deliverychargeinp.value != ""){
        updateSumTotalFendBend(setfocusid="delivery_charge_input");
        // }
    });

    searchbillsinput.addEventListener('input', function(){
        updateSearchBillsFendBend();
    });

    searchbillsdatecb.addEventListener('input', function(){
        updateSearchBillsFendBend();
    });

    searchbillscnamecb.addEventListener('input', function(){
        updateSearchBillsFendBend();
    });

    searchbillskotcb.addEventListener('input', function(){
        updateSearchBillsFendBend();
    });       

    loadItemsListFend();
    updateSearchBillsFendBend();
});

async function openGeneratedBills(){
    
    var billid_string = prompt("Bill Id: ");
    let savedbill_exists = await eel.does_bill_exist(billid_string)();
    if(savedbill_exists == "exists"){
        eel.openGeneratedBills(billid_string)();
    } else{
        alert("Bill Id Invalid!!!");
    }
    
}

async function updatePaymentStatus(){
    
    let update = eel.updatePaymentStatus()();
    
    
}

async function updateSearchBillsFendBend(){
    const datecbox = document.getElementById("datecbox_filter");
    const cnamecbox = document.getElementById("cnamecbox_filter");
    const kotcbox = document.getElementById("kotcbox_filter");
    const searchinputbox = document.getElementById("searchbills");
    const billinglistparentcont = document.getElementById("billinglist_filtered");
    let datebillsearchres = [];
    let cnamebillsearchres = [];
    let kotbillsearchres = [];
    let allsearchres = [];
    billinglistparentcont.innerHTML = "";
    if (datecbox.checked){
        datebillsearchres = await eel.searchbills(searchinputbox.value, "date")();
        datebillsearchres.forEach(searchresitem => {
            var newsearchresdiv = document.createElement("div");
            newsearchresdiv.className = "billlist-itemclass";
            newsearchresdiv.id = searchresitem[0] + "billlistitem";
            newsearchresdiv.textContent = searchresitem[0] + " " + searchresitem[1];
            newsearchresdiv.onclick = function(){
                openBillById(searchresitem[0]);
            };
            billinglistparentcont.appendChild(newsearchresdiv);
        });
    }
    if (cnamecbox.checked){
        cnamebillsearchres = await eel.searchbills(searchinputbox.value, "cname")();
        cnamebillsearchres.forEach(searchresitem => {
            var newsearchresdiv = document.createElement("div");
            newsearchresdiv.className = "billlist-itemclass";
            newsearchresdiv.id = searchresitem[0] + "billlistitem";
            newsearchresdiv.textContent = searchresitem[0] + " " + searchresitem[1];
            newsearchresdiv.onclick = function(){
                openBillById(searchresitem[0]);
            };
            billinglistparentcont.appendChild(newsearchresdiv);
        });
    }
    if (kotcbox.checked){
        kotbillsearchres = await eel.searchbills(searchinputbox.value, "kotnum")();
        kotbillsearchres.forEach(searchresitem => {
            var newsearchresdiv = document.createElement("div");
            newsearchresdiv.className = "billlist-itemclass";
            newsearchresdiv.id = searchresitem[0] + "billlistitem";
            newsearchresdiv.textContent = searchresitem[0] + " " + searchresitem[1];
            newsearchresdiv.onclick = function(){
                openBillById(searchresitem[0]);
            };
            billinglistparentcont.appendChild(newsearchresdiv);
        });
    }

    if (!datecbox.checked && !cnamecbox.checked && !kotcbox.checked){
        allsearchres = await eel.searchbills("", "")();
        allsearchres.forEach(searchresitem => {
            var newsearchresdiv = document.createElement("div");
            newsearchresdiv.className = "billlist-itemclass";
            newsearchresdiv.id = searchresitem[0] + "billlistitem";
            newsearchresdiv.textContent = searchresitem[0] + " " + searchresitem[1];
            newsearchresdiv.onclick = function(){
                openBillById(searchresitem[0]);
            };
            billinglistparentcont.appendChild(newsearchresdiv);
        });
    }
    // allsearchres.concat(datebillsearchres, cnamebillsearchres, kotbillsearchres);

    
    // alert(allsearchres);
    
}

async function newBillClicked(){
    
    let new_bill_id = await eel.getNewBillID()();
    let todate = await eel.getTodate()();

    current_billno = new_bill_id;
    current_roomnums = [];
    current_kotnums = [];
    allitemslist = []
    showingitemslist = []
    newbill = new Map();
    itemcount = 1
    // var temptotal = 0
    discount_percent = 0;
    delivery_charges = 0;
    
    document.getElementById("delivery_charge_input").value = 0;
    document.getElementById("discount_percent_input").value = 0;

    sumtotal = 0;

    const billnodiv = document.getElementById("bno_text");
    const datediv = document.getElementById("date_input");

    billnodiv.textContent = current_billno;
    datediv.value = todate;
    set_fend_to_dictvalues();
    clear_kotnums();
    clear_roomnums();
    var customnameinp_field = document.getElementById("newitemname_tbox");
    var customrateinp_field = document.getElementById("newitemrate_tbox");
    var customqtyinp_field = document.getElementById("newitemqty_tbox");
    var customernamefield = document.getElementById("cust_name_input");
    customnameinp_field.value = "";
    customrateinp_field.value = "";
    customqtyinp_field.value = "";
    customernamefield.value = "";

}

async function generateBillOfficeCopy(){
    saveCurrentBill();
    let officecopy = eel.generate_bill_officecopy(document.getElementById("bno_text").textContent)();
    let customercopy = eel.generate_bill_customercopy(document.getElementById("bno_text").textContent)();
}

async function showPrevBill(){
    var current_billno_text = document.getElementById("bno_text").textContent;
    if(current_billno_text != null || current_billno_text.trim() != ""){
        var prevBillNo = await eel.prevBillNo(current_billno_text)();
        let billexists = await eel.does_bill_exist(prevBillNo)();
        if(billexists == "exists"){
            openBillById(prevBillNo);
        }
    }
}

async function showNextBill(){
    var current_billno_text = document.getElementById("bno_text").textContent;
    if(current_billno_text != null || current_billno_text.trim() != ""){
        var nextBillNo = await eel.nextBillNo(current_billno_text)();
        let billexists = await eel.does_bill_exist(nextBillNo)();
        if(billexists == "exists"){
            openBillById(nextBillNo);
        }
    }
}


async function openBillById(billidparam=null){
    let open_billid = billidparam;
    eel.billGeneratedCheck(open_billid)();
    if(billidparam==null){
        open_billid = prompt("Enter Bill No. to Open", "0000");
    } else{
    }
    if(open_billid != null || open_billid != ""){
        let bill_exists = await eel.does_bill_exist(open_billid)();
        if(bill_exists == "exists"){
            let billdat = await eel.fetchBillDataById(open_billid)();

            current_billno = open_billid;
            current_roomnums = [];
            current_kotnums = [];
            allitemslist = []
            showingitemslist = []
            newbill = new Map();
            itemcount = 1
            // var temptotal = 0
            discount_percent = 0;
            delivery_charges = 0;

            document.getElementById("delivery_charge_input").value = 0;
            document.getElementById("discount_percent_input").value = 0;

            sumtotal = 0;
            current_customername = "";
        
            const billnodiv = document.getElementById("bno_text");
            const datediv = document.getElementById("date_input");
        
            billnodiv.textContent = current_billno;
            datediv.value = "";
            set_fend_to_dictvalues();
            clear_kotnums();
            clear_roomnums();
            var customnameinp_field = document.getElementById("newitemname_tbox");
            var customrateinp_field = document.getElementById("newitemrate_tbox");
            var customqtyinp_field = document.getElementById("newitemqty_tbox");
            var customernamefield = document.getElementById("cust_name_input");
            customnameinp_field.value = "";
            customrateinp_field.value = "";
            customqtyinp_field.value = "";
            customernamefield.value = "";

            current_roomnums = billdat[3];
            update_Rooms_fend();

            current_kotnums = billdat[4];
            update_Kots_fend();
            
            current_customername = billdat[2];
            document.getElementById("cust_name_input").value = current_customername;
            
            document.getElementById("date_input").value = billdat[1];
            
            discount_percent = Number(billdat[5]);
            document.getElementById("discount_percent_input").value = discount_percent;
            
            delivery_charges = Number(billdat[6]);
            document.getElementById("delivery_charge_input").value = delivery_charges;
            
            sumtotal = billdat[7];
            document.getElementById("sum_total").value = sumtotal;

            billdat[8].forEach(billeditem => {
                newbill.set(billeditem[1], [itemcount, billeditem[0], Number(billeditem[2]), Number(billeditem[3]), Number(billeditem[4])]);
            });
            set_fend_to_dictvalues();
        } else{
            alert("Bill number Not Found in Database!!!");
        }
    }
}

function saveCurrentBill(){
    // alert(newbill);
    var keylist = newbill.keys();
    var newbill_objectlist = [];
    newbill.keys().forEach(itemkey => {
        var this_itemarr = newbill.get(itemkey)
        this_itemarr.push(itemkey);
        newbill_objectlist.push(this_itemarr);
    });
    var dateval = document.getElementById("date_input").value;
    eel.newBill(current_billno,
        current_customername,
        current_kotnums,
        current_roomnums,
        keylist,
        newbill_objectlist,
        discount_percent,
        delivery_charges,
        sumtotal,
        dateval
    );
    alert("Bill saved to database");
}

async function billNewItem_customitem(){
    var customnameinp_field = document.getElementById("newitemname_tbox");
    var customrateinp_field = document.getElementById("newitemrate_tbox");
    var customqtyinp_field = document.getElementById("newitemqty_tbox");
    var customitemname = customnameinp_field.value;
    var customitemrate = customrateinp_field.value;
    var customitemqty = customqtyinp_field.value;

    if(customitemname.trim() == "" || customitemrate.trim() == ""){
        alert("All new item fields require value!!")
        return
    }
    if(customitemqty.trim() == ""){
        customitemqty = 0;
    }
    let rand_id = await eel.getrandid()();

    if(!newbill.has(rand_id)){
        var alldets = [itemcount, customitemname, customitemrate, customitemqty, Number(customitemrate) * Number(customitemqty)];
        // itemcount = itemcount + 1;
        newbill.set(rand_id, alldets);
        // addToSummary([itemid, itemcount, defaultdets[1], defaultdets[2], 0, 0]);
        set_fend_to_dictvalues();
    }
    customnameinp_field.value = "";
    customrateinp_field.value = "";
    customqtyinp_field.value = "";
}

function updateSumTotalFendBend(setfocusid=null){
    discount_percent = document.getElementById("discount_percent_input").value;
    delivery_charges = document.getElementById("delivery_charge_input").value;
    var temptotal = 0;
    newbill.keys().forEach(billeditemkey => {
        itemtotal_this = newbill.get(billeditemkey)[4];
        temptotal = temptotal + itemtotal_this;
    });
    discountamount = (discount_percent/100)*temptotal
    // alert(discountamount)
    sumtotal = temptotal - discountamount + Number(delivery_charges);
    // alert(temptotal);
    document.getElementById("sum_total").value = sumtotal;
    if(setfocusid != null){
        document.getElementById(setfocusid).focus();
    }
}

async function menusearchBendFend(searchcriteria){
    let searchres = await eel.menusearch(searchcriteria)();
    var menuitemslist = document.getElementById("itemslist_filtered")
    menuitemslist.innerHTML = "";
    searchres.forEach(itemtext => {
        newitemdiv = document.createElement("div");
        newitemdiv.textContent = itemtext;
        newitemdiv.className = "menulist-itemclass";
        newitemdiv.id = itemtext.split(" ")[0].trim();
        newitemdiv.onclick = function(){
            pushToBill(itemtext.split(" ")[0].trim());
        };
        menuitemslist.appendChild(newitemdiv);
    });
    return
}

async function pushToBill(itemid){
    // alert("pushtobill" + itemid)
    if(!newbill.has(itemid)){
        let defaultdets = await eel.getDefaultDets(itemid)();
        // itemcount = itemcount + 1;
        newbill.set(itemid, [itemcount, defaultdets[1], defaultdets[2], 1, defaultdets[2]]);
        // addToSummary([itemid, itemcount, defaultdets[1], defaultdets[2], 0, 0]);
        set_fend_to_dictvalues();
    }
}

function addToSummary(itemdets_arr){
    var summaryparentcont = document.getElementById("billsummaryparentact");
    
    var newitem_contdiv = document.createElement("div");
    newitem_contdiv.className = "billeditem_cont";
    newitem_contdiv.id = itemdets_arr[0] + "newitemcontdiv";

    var newitem_slno = document.createElement("div");
    newitem_slno.className = "slno_billsummary_class";
    newitem_slno.textContent = itemdets_arr[1];

    var newitem_itemname = document.createElement("div");
    newitem_itemname.className = "itemname_billsummary_class";
    newitem_itemname.textContent = itemdets_arr[2];

    var newitem_itemrate = document.createElement("div");
    newitem_itemrate.className = "rate_billsummary_class";
    var newitem_rate_tbox = document.createElement("input");
    newitem_rate_tbox.type = "text";
    newitem_rate_tbox.id = "rate_bill_input_" + itemdets_arr[0]
    newitem_rate_tbox.className = "text-input-rate_billsummary";
    newitem_rate_tbox.value = itemdets_arr[3];
    newitem_rate_tbox.readOnly = true;
    newitem_itemrate.appendChild(newitem_rate_tbox);

    var newitem_itemqty = document.createElement("div");
    newitem_itemqty.className = "qty_billsummary_class";
    var newitem_qty_tbox = document.createElement("input");
    newitem_qty_tbox.type = "text";
    newitem_qty_tbox.id = "qty_bill_input_" + itemdets_arr[0]
    newitem_qty_tbox.className = "text-input-qty_billsummary";
    newitem_qty_tbox.value = itemdets_arr[4];
    newitem_qty_tbox.addEventListener('input', function() {
        if (newitem_qty_tbox.value.trim() != "") {
            var new_qty = newitem_qty_tbox.value.trim();
            var item_innewbill = newbill.get(itemdets_arr[0]);
            item_innewbill[3] = new_qty;
            item_innewbill[4] = item_innewbill[2] * item_innewbill[3];
            newbill.set(itemdets_arr[0], item_innewbill);
            set_fend_to_dictvalues(focusid="qty_bill_input_"+itemdets_arr[0]);

        }
    });
    newitem_itemqty.appendChild(newitem_qty_tbox);

    var newitem_itemamount = document.createElement("div");
    newitem_itemamount.className = "amount_billsummary_class";
    var newitem_amount_tbox = document.createElement("input");
    newitem_amount_tbox.type = "text";
    newitem_amount_tbox.id = "amount_bill_input_" + itemdets_arr[0]
    newitem_amount_tbox.className = "text-input-qty_billsummary";
    newitem_amount_tbox.value = itemdets_arr[3] * itemdets_arr[4];
    newitem_amount_tbox.readOnly = true;
    newitem_itemamount.appendChild(newitem_amount_tbox);

    var newitem_removeitem_div = document.createElement("div");
    newitem_removeitem_div.className = "delitem_billsummary_class";
    newitem_removeitem_div.textContent = "X";
    newitem_removeitem_div.onclick = function(){
        remove_from_bill(itemdets_arr[0]);
    };

    newitem_contdiv.appendChild(newitem_slno);
    newitem_contdiv.appendChild(newitem_itemname);
    newitem_contdiv.appendChild(newitem_itemrate);
    newitem_contdiv.appendChild(newitem_itemqty);
    newitem_contdiv.appendChild(newitem_itemamount);
    newitem_contdiv.appendChild(newitem_removeitem_div);

    summaryparentcont.appendChild(newitem_contdiv);
    
}

function fix_newbill_itemorder(){
    itemcountupdated = 1
    newbill.keys().forEach(itemkey => {
        this_itemarray = newbill.get(itemkey);
        this_itemarray[0] = itemcountupdated;
        itemcountupdated = itemcountupdated + 1
        newbill.set(itemkey, this_itemarray);
    });
    itemcount = itemcountupdated;
}

function set_fend_to_dictvalues(focusid=null){
    fix_newbill_itemorder();
    updateSumTotalFendBend();
    var billsummaryparentcont = document.getElementById("billsummaryparentact");
    billsummaryparentcont.innerHTML = "";
    newbill.keys().forEach(itemkey => {
        var itemarray = [itemkey, newbill.get(itemkey)[0], newbill.get(itemkey)[1], newbill.get(itemkey)[2], newbill.get(itemkey)[3], newbill.get(itemkey)[4]];
        addToSummary(itemarray);
    });
    if(focusid!=null){
        document.getElementById(focusid).focus();
    }
}

function remove_from_bill(remove_itemid){
    var summaryparentcont = document.getElementById("billsummaryparentact");
    var itemcontdiv = document.getElementById(remove_itemid + "newitemcontdiv");
    summaryparentcont.removeChild(itemcontdiv);
    itemcount = itemcount - 1;
    newbill.delete(remove_itemid);
    fix_newbill_itemorder();
    set_fend_to_dictvalues();
}

async function loadItemsListFend(){
    let itemslist = await eel.getAllItemsList()();
    var menuitemslist = document.getElementById("itemslist_filtered")
    menuitemslist.innerHTML = "";
    itemslist.forEach(itemtext => {
        newitemdiv = document.createElement("div");
        newitemdiv.textContent = itemtext;
        newitemdiv.className = "menulist-itemclass";
        newitemdiv.id = itemtext.split(" ")[0].trim();
        newitemdiv.onclick = function(){
            pushToBill(itemtext.split(" ")[0].trim());
        };
        menuitemslist.appendChild(newitemdiv);
    });
    return
}

function update_Rooms_fend(){
    // alert(room_num);
    var enteredroomnumsdiv = document.getElementById("entered_room_nums");
    enteredroomnumsdiv.innerHTML = "";
    current_roomnums.forEach(roomnum => {
        var newroomentered_div = document.createElement("div");
        newroomentered_div.className = "enteredroomnumdiv_class";
        newroomentered_div.textContent = roomnum;
        enteredroomnumsdiv.appendChild(newroomentered_div); 
    });
    return
}

function clear_roomnums(){
    current_roomnums = [];
    update_Rooms_fend();
}


function update_Kots_fend(){
    // alert(room_num);
    var enteredkotnumsdiv = document.getElementById("entered_kot_nums");
    enteredkotnumsdiv.innerHTML = "";
    current_kotnums.forEach(kotnum => {
        var newkotentered_div = document.createElement("div");
        newkotentered_div.className = "enteredkotnumdiv_class";
        newkotentered_div.textContent = kotnum;
        enteredkotnumsdiv.appendChild(newkotentered_div); 
    });
    return
}

function clear_kotnums(){
    current_kotnums = [];
    update_Kots_fend();
}