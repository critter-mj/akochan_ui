async function show_log(view_pid, can_click) {
    let log_json = await eel.get_log(view_pid)();
    var table_str = '<table id="log_table" class="log_table">\n';
    for (let i = 0; i < log_json.length; i++) {
        table_str += '<tr><td class="log_num">' + String(i) + '</td><td class="log_action">';
        if (can_click) {
            table_str += '<a href="#" onclick="log_pos_selected(' + String(i) + ')">' + JSON.stringify(log_json[i]) + '</a>';
        } else {
            table_str += JSON.stringify(log_json[i]);
        }
        table_str += '</td></tr>\n'; 
    }
    table_str += '</table>\n';
    document.getElementById("log_table_container").innerHTML = table_str;
}

function reset_button_ui_log() {
    document.getElementById("default_button_ui").innerHTML = '';
    document.getElementById("default_button_ui").innerHTML += '<li class="button_ui_item"><a href="#" onclick="change_view_pid(-1)">上家</a></li>';
    document.getElementById("default_button_ui").innerHTML += '<li class="button_ui_item"><a href="#" onclick="change_view_pid(1)">下家</a></li>';
}

async function unhighlight_log_pos() {
    let log_pos = await eel.get_log_pos()();
    var cell = document.getElementById("log_table").rows[log_pos].cells[1];
    cell.outerHTML = cell.outerHTML.replace('log_selected_action', 'log_action');
}

function highlight_log_pos(pos) {
    var cell = document.getElementById("log_table").rows[pos].cells[1];
    cell.outerHTML = cell.outerHTML.replace('log_action', 'log_selected_action');
}

async function log_pos_selected(pos) {
    unhighlight_log_pos();
    let state_json = await eel.log_pos_selected(pos)();
    let view_pid = await eel.get_view_pid()();
    update_board(state_json, view_pid);
    highlight_log_pos(pos);
}

async function change_view_pid(add) {
    let view_pid = await eel.change_view_pid(add)();
    let state_json = await eel.get_game_state(-1)();
    update_board(state_json, view_pid);
}