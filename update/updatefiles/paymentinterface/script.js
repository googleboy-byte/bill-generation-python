let paymentrecordmap = new Map();
var paymentrecordcount = 1;
var currentbill_paid = 0;
var currentbill_due = 0;
var currentbill_billedamount = 5000;
var currentbill_billno = "";
var currentbill_custname = "UNKNOWN";
let modalelem = document.getElementById("modal-overlay");


// document.addEventListener("DOMContentLoaded", function(){
//     // loadfirst();
    
// });

async function genSummary_bno(startingbno, endingbno){
    let firstexists = await eel.does_bill_exist_payment(String(startingbno).trim())();
    let secondexists = await eel.does_bill_exist_payment(String(endingbno).trim())();
    if(firstexists != "exists" || secondexists != "exists"){
        alert("Invalid bill number range!!!");
        return
    }
    let gensumretmsg = await eel.gensummary_bno(startingbno, endingbno)();
    alert(gensumretmsg);
    let firstelem = document.getElementById("billsummary_startbno");
    let secondelem = document.getElementById("billsummary_endbno");
    firstelem.value = "";
    secondelem.value = "";
    modalelem.style.display = "none";
}

function openBillNoSummaryModal_days(){
    document.getElementById('modalOverlay1').style.display = 'flex';
}

function openBillNoSummaryModal(){
    document.getElementById('modalOverlay').style.display = 'flex';
}

async function genSummary_ndays(ndays){
    let gensumndaysret = await eel.gensummary_lastndays(Number(ndays))();
    alert(gensumndaysret);
}

async function loadfirst(){
    let firstload_billno = eel.getFirstPaymentLoadBillNo()();
    load_billno_payment(firstload_billno);
}

async function addPayment(){
    if(currentbill_billno != ""){
        let todate_addpayment = await eel.getTodate()();
        paymentrecordmap.set(paymentrecordcount + 1, ["cashmethod", todate_addpayment, "5000.00", ""]);
        paymentrecordcount = paymentrecordcount + 1;
        updatePaymentFend();   
        // alert(paymentrecordmap.keys()); 
    }
}

function removePaymentRecord(payment_elementid){
    paymentrecordmap.delete(payment_elementid);
    // correct_paymentrecordmap_order(); // needless since updatePaymentFend corrects the order by itself as method is called
    updatePaymentFend();
}

function correct_paymentrecordmap_order(){
    let tempnewmap = new Map();
    let newcount = 1;
    paymentrecordmap.forEach((value, key) => {
        tempnewmap.set(newcount, value);
        newcount = newcount + 1;
    });
    paymentrecordmap = tempnewmap;
}

async function updatePaymentRecord(){
    let sendlist_prmap = [];
    paymentrecordmap.forEach((value, key) => {
        sendlist_prmap.push(value);
    });
    let updateretmsg = await eel.updatePayment_db(sendlist_prmap, currentbill_billno, currentbill_billedamount, currentbill_due)();
    alert(updateretmsg);
}

function update_due_paid_vals(){
    var paidamountdisplay_element = document.getElementById("paidamount_display");
    var dueamountdisplay_element = document.getElementById("dueamount_display");
    currentbill_paid = calculate_currentbillpaid();
    currentbill_due = calculate_currentbilldue();
    paidamountdisplay_element.textContent = currentbill_paid;
    dueamountdisplay_element.textContent = currentbill_due;

}

async function updatePaymentFend(){


    let focusid = document.activeElement.id;

    var bnodisplayelement = document.getElementById("bno_text_display");
    var custnameelement = document.getElementById("cust_name_display");
    var billedamountdisplay_element = document.getElementById("billedamount_display");
    var paidamountdisplay_element = document.getElementById("paidamount_display");
    var dueamountdisplay_element = document.getElementById("dueamount_display");

    bnodisplayelement.textContent = currentbill_billno;
    custnameelement.value = currentbill_custname;
    billedamountdisplay_element.textContent = currentbill_billedamount;
    currentbill_paid = calculate_currentbillpaid();
    currentbill_due = calculate_currentbilldue();
    paidamountdisplay_element.textContent = currentbill_paid;
    dueamountdisplay_element.textContent = currentbill_due;

    
    var paymentrecords_ParentCont = document.getElementById("paymentSummaryParentCont");
    paymentrecords_ParentCont.innerHTML = "";

    // var todate = await eel.getTodate()();

    correct_paymentrecordmap_order();

    paymentrecordmap.forEach((paymentdets, key) => { 
        // paymentdets -> [paymentmode, date, amount, comment]
        var recordrow = document.createElement("div");
        recordrow.className = "paymentrecordrow";
        recordrow.id = String(key) + "recordrow";

        // add payment methods
        var pmethods = document.createElement("select");
        pmethods.id = String(key) + "pmethods";

        var cashmethod = document.createElement("option");
        cashmethod.value = "cashmethod";
        cashmethod.textContent = "Cash";

        var upimethod = document.createElement("option");
        upimethod.value = "upimethod";
        upimethod.textContent = "UPI";

        var cardmethod = document.createElement("option");
        cardmethod.value = "cardmethod";
        cardmethod.textContent = "Card";

        var btransfermethod = document.createElement("option");
        btransfermethod.value = "btransfermethod";
        btransfermethod.textContent = "Bank Transfer";

        pmethods.appendChild(cashmethod);
        pmethods.appendChild(upimethod);
        pmethods.appendChild(cardmethod);
        pmethods.appendChild(btransfermethod);

        if(paymentdets[0] == "cashmethod"){
            pmethods.options[0].selected = true;
        }
        if(paymentdets[0] == "upimethod"){
            pmethods.options[1].selected = true;
        }
        if(paymentdets[0] == "cardmethod"){
            pmethods.options[2].selected = true;
        }
        if(paymentdets[0] == "btransfermethod"){
            pmethods.options[3].selected = true
        }

        pmethods.addEventListener('input', function() {
            var new_pmethod = pmethods.value;
            var item_in_paymentrec = paymentrecordmap.get(key);
            item_in_paymentrec[0] = new_pmethod;
            paymentrecordmap.set(key, item_in_paymentrec);
            updatePaymentFend();
        });

        recordrow.appendChild(pmethods);

        var date_input_box = document.createElement("input");
        date_input_box.type = "text";
        date_input_box.id = String(key) + "dateinputbox";
        date_input_box.className = "text-input";
        date_input_box.placeholder = "dd/mm/yyyy";
        date_input_box.value = paymentdets[1];
        date_input_box.addEventListener('input', function() {
            var new_date = date_input_box.value.trim();
            var item_in_paymentrec = paymentrecordmap.get(key);
            item_in_paymentrec[1] = new_date;
            paymentrecordmap.set(key, item_in_paymentrec);
            // updatePaymentFend();
        });// --> change this to fit this code


        recordrow.appendChild(date_input_box);

        var amountinputbox = document.createElement("input");
        amountinputbox.type = "number";
        amountinputbox.step = "0.01";
        amountinputbox.id = String(key) + "amountinputbox";
        amountinputbox.className = "text-input";
        amountinputbox.placeholder = "Amount (in Rs.)";
        amountinputbox.value = paymentdets[2];
        amountinputbox.addEventListener('input', function() {
            var new_amount = amountinputbox.value.trim();
            var item_in_paymentrec = paymentrecordmap.get(key);
            item_in_paymentrec[2] = new_amount;
            paymentrecordmap.set(key, item_in_paymentrec);
            update_due_paid_vals();
        });// --> change this to fit this code
        amountinputbox.addEventListener('blur', (event) => {
            const value = parseFloat(event.target.value).toFixed(2);

            if (!isNaN(value)) {
                // Format to two decimal places
                event.target.value = value
                var item_in_paymentrec = paymentrecordmap.get(key);
                item_in_paymentrec[2] = value;
                paymentrecordmap.set(key, item_in_paymentrec);
                update_due_paid_vals();
            }
        });


        recordrow.appendChild(amountinputbox);

        var commentinputbox = document.createElement("input");
        commentinputbox.type = "text";
        commentinputbox.id = String(key) + "commentinputbox";
        commentinputbox.className = "text-input";
        commentinputbox.placeholder = "Comment...";
        commentinputbox.value = paymentdets[3]
        commentinputbox.addEventListener('input', function() {
            var new_comment = commentinputbox.value;
            var item_in_paymentrec = paymentrecordmap.get(key);
            item_in_paymentrec[3] = new_comment;
            paymentrecordmap.set(key, item_in_paymentrec);
            // updatePaymentFend();
        });// --> change this to fit this code


        recordrow.appendChild(commentinputbox);

        var removebtndiv = document.createElement("div");
        removebtndiv.className = "delitem_billsummary_class";
        removebtndiv.textContent = "X";
        removebtndiv.onclick = function(){
            removePaymentRecord(key);
        };

        recordrow.appendChild(removebtndiv);

        paymentrecords_ParentCont.appendChild(recordrow);
        try {
            document.getElementById(focusid).focus();
        } catch (error) {
            console.log(error);
        }
    });
}

function calculate_currentbillpaid(){
    var sum = 0;
    paymentrecordmap.forEach((paymentdetails, key) => {
        sum = sum + Number(paymentdetails[2]);
    });
    return sum;
}

function calculate_currentbilldue(){
    var paidamount = calculate_currentbillpaid();
    return Number(currentbill_billedamount) - paidamount;
}

async function showPrevBillPayment(){
    if(currentbill_billno != ""){
        let prevbillno = await eel.prevBillNo(currentbill_billno)();
        load_billno_payment(prevbillno);
    }
}

async function showNextBillPayment(){
    if(currentbill_billno != ""){
        let nextbillno = await eel.nextBillNo(currentbill_billno)();
        load_billno_payment(nextbillno);
    }
}

async function gotoBillPayment(){
    let billid = prompt("Enter Bill No.");
    load_billno_payment(billid);
}

async function load_billno_payment(billno_id){
    // do this next
    // alert("loading billno" + billno_id);
    let billexists = await eel.does_bill_exist_payment(String(billno_id).trim())();
    if(billexists=="exists"){
        let paymentdata_from_db = await eel.getPaymentStatusData(billno_id)();
        // alert("bill fetched");
        var paymentmethods = paymentdata_from_db[0];
        var paymentdates = paymentdata_from_db[1];
        var paymentamounts = paymentdata_from_db[2];
        var paymentcomments = paymentdata_from_db[3];
        // var dueamount = paymentdata_from_db[4];
        var billedamount = paymentdata_from_db[5];
        var custname = paymentdata_from_db[7];

        // paymentdets -> [paymentmode, date, amount, comment]
        
        // update global current bill vars

        // generate paymentrecordmap
        let paymentindexcount = 1;
        // alert(paymentmethods);
        paymentrecordmap = new Map();
        for (let index = 0; index < paymentmethods.length; index++) {
            paymentrecordmap.set(paymentindexcount, [paymentmethods[index], paymentdates[index], paymentamounts[index], paymentcomments[index]]);
            paymentindexcount = paymentindexcount + 1;
        }

        // other global vars set

        currentbill_billedamount = billedamount;
        currentbill_billno = billno_id;
        currentbill_custname = custname;
        paymentrecordcount = paymentindexcount - 1; // 0 based indexing --> for in in range (i = 0, i < paymentrecordcount)
        // alert("global vars updated");
        updatePaymentFend();
    } else{
        alert("Invalid Bill Id");
    }



}
