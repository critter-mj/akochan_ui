eel.expose(update_game_child2)
function update_game_child2(state_json, view_pid) {
    update_tehai_ui(state_json, view_pid);
    let state_json_dcp = JSON.parse(JSON.stringify(state_json));
    // プレイヤーの手牌を非表示にする。
    // ここで要素を消したことが、update_tehai_uiの方に悪さをしないようにdeep copyしておく。
    state_json_dcp["player_state"][view_pid]["tehai"] = [];
    delete state_json_dcp["player_state"][view_pid]["current_tsumo"];
    update_board(state_json_dcp, view_pid);
}

async function update_game_child() {
    let view_pid = await eel.get_view_pid()();
    let state_json = await eel.get_game_state(view_pid)();
    update_game_child2(state_json, view_pid);
}

eel.expose(update_game)
function update_game(view_pid) {
    update_game_child();
    show_log(view_pid, false);

    var obj = document.getElementById("log_table_container");
    obj.scrollTop = obj.scrollHeight;
    // 何故か最下部は見えないが妥協。
}

function get_tehai_ui_tags(tehai, current_tsumo) {
    ret = [];
    for (var i = 0; i < tehai.length; i++) {
        tag = '<img class="repeated pai_large pai_tehai_ui"';
        tag += ' style="display: inline;"';
        tag += ' onclick="tehai_clicked(' + String(i) + ')"';
        tag += ' src="img/' + tehai[i] + '_0.png">';
        ret.push(tag);
    }
    if (current_tsumo != null) {
        tag = '<img class="tsumo-pai pai_large pai_tehai_ui"';
        tag += ' style="display: inline;"';
        tag += ' onclick="tehai_clicked(' + String(tehai.length) + ')"';
        tag += ' src="img/' + current_tsumo + '_0.png">';
        ret.push(tag);
    } else {
        ret.push('<img class="tsumo-pai" style="display: none;">');
    }
    for (var i = tehai.length; i < 13; i++) {
        ret.push('<img class="tsumo-pai" style="display: none;">');
    }
    return ret;
}

function update_tehai_ui(state_json, view_pid) {
    let ps = state_json["player_state"][view_pid];
    let current_tsumo = null;
    if ("current_tsumo" in ps) {
        current_tsumo = ps["current_tsumo"];
    }
    let tags = get_tehai_ui_tags(ps["tehai"], current_tsumo);
    console.log(tags);
    let tehai_ui = document.getElementById("tehai_ui");
    if (tehai_ui.children.length == 14) {
        for (var i = 0; i < 14; i++) {
            if (tehai_ui.children[i].outerHTML != tags[i]) {
                tehai_ui.children[i].outerHTML = tags[i];
            }
        }
    } else {
        document.getElementById("tehai_ui").innerHTML = '';
        for (var i = 0; i < 14; i++) {
            document.getElementById("tehai_ui").innerHTML += tags[i];
        }
    }
}

eel.expose(reset_button_ui_game)
function reset_button_ui_game() {
    document.getElementById("default_button_ui").innerHTML = '';
    document.getElementById("default_button_ui").innerHTML += '<li id="hora_button" class="button_ui_item">和了</li>';
    document.getElementById("default_button_ui").innerHTML += '<li id="reach_button" class="button_ui_item">リーチ</li>';
    document.getElementById("default_button_ui").innerHTML += '<li id="daiminkan_button" class="button_ui_item">大明槓</li>';
    document.getElementById("default_button_ui").innerHTML += '<li id="pass_button" class="button_ui_item">パス</li>';
    document.getElementById("default_button_ui").innerHTML += '<li id="ryukyoku_button" class="button_ui_item">流局</li>';

    document.getElementById("kan_button_ui").innerHTML = '';
}

eel.expose(activate_hora_button)
function activate_hora_button() {
    document.getElementById("hora_button").innerHTML = '<a href="#" onclick="hora_clicked()">和了</a>';
}

eel.expose(activate_reach_button)
function activate_reach_button() {
    document.getElementById("reach_button").innerHTML = '<a href="#" onclick="reach_clicked()">リーチ</a>';
}

eel.expose(activate_daiminkan_button)
function activate_daiminkan_button() {
    document.getElementById("daiminkan_button").innerHTML = '<a href="#" onclick="daiminkan_clicked()">大明槓</a>';
}

eel.expose(activate_pass_button)
function activate_pass_button() {
    document.getElementById("pass_button").innerHTML = '<a href="#" onclick="pass_clicked()">パス</a>';
}

eel.expose(activate_ryukyoku_button)
function activate_ryukyoku_button() {
    document.getElementById("ryukyoku_button").innerHTML = '<a href="#" onclick="ryukyoku_clicked()">流局</a>';
}

eel.expose(append_ankan_button)
function append_ankan_button(pai_str) {
    document.getElementById("kan_button_ui").innerHTML += '<li class="button_ui_item"><a href="#" onclick="ankan_clicked(\'' + pai_str + '\')">暗槓<img class="kan-icon pai" src="img/' + pai_str + '_0.png"></a></li>';
}

eel.expose(append_kakan_button)
function append_kakan_button(pai_str) {
    document.getElementById("kan_button_ui").innerHTML += '<li class="button_ui_item"><a href="#" onclick="kakan_clicked(\'' + pai_str + '\')">加槓<img class="kan-icon pai" src="img/' + pai_str + '_0.png"></a></li>';
}

eel.expose(show_end_kyoku)
function show_end_kyoku(action_json) {
    info_str = '<div>';
    if (action_json["type"] == "hora") {
        info_str += '和了 actor: ' + action_json["actor"] + ' target: ' + action_json["target"];
    } else if (action_json["type"] == "ryukyoku" && action_json["reason"] == "fanpai") {
        info_str += '流局'
    } else if (action_json["type"] == "ryukyoku" && action_json["reason"] == "kyushukyuhai") {
        info_str += '流局（九種九牌） actor: ' + action_json["actor"];
    }
    info_str += '</div>';

    hora_str = '<div>';
    if (action_json["type"] == "hora") {
        hora_str += action_json["fan"] + ' 翻 ' + action_json["fu"] + ' 符 ';
        if ("uradora_marker" in action_json) {
            hora_str += ' 裏ドラ表示: ';
            for (var i = 0; i < action_json["uradora_marker"].length; i++) {
                hora_str += '<img class="pai" style="display: inline;" src="img/' + action_json["uradora_marker"][i] + '_0.png">';
            }
        }
    }
    hora_str += '</div>';

    tehai_str = '<div>';
    if (action_json["type"] == "hora") {
        tehai_str += '<img class="repeated">';
        for (var i = 0; i < action_json["hora_tehais"].length; i++) {
            tehai_str += '<img class="repeated pai_large" style="display: inline;" src="img/' + action_json["hora_tehais"][i] + '_0.png">';
        }
        tehai_str += '<img class="tsumo-pai pai_large" style="display: inline;" src="img/' + action_json["pai"] + '_0.png">';
    } else if (action_json["type"] == "ryukyoku" && action_json["reason"] == "fanpai") {
        tehai_str += '<table class="ryukyoku_tehai_table">'
        for (var pid = 0; pid < 4; pid++) {
            tehai_str += '<tr><td>';
            for (var i = 0; i < action_json["tehais"][pid].length; i++) {
                if (action_json["tehais"][pid][i] == '?') {
                    tehai_str += '<img class="repeated pai_large" style="display: inline;" src="img/0_0.png">';
                } else {
                    tehai_str += '<img class="repeated pai_large" style="display: inline;" src="img/' + action_json["tehais"][pid][i] + '_0.png">';
                }
            }
            tehai_str += '</td></tr>';
        }
        tehai_str += '</table>';
    } else if (action_json["type"] == "ryukyoku" && action_json["reason"] == "kyushukyuhai") {
        tehai_str += '<img class="repeated">';
        let actor = action_json["actor"];
        for (var i = 0; i < action_json["tehais"][actor].length; i++) {
            tehai_str += '<img class="repeated pai_large" style="display: inline;" src="img/' + action_json["tehais"][actor][i] + '_0.png">';
        }
    }
    tehai_str += '</div>';

    table_str = '<div><table class="ryukyoku_score_table">';
    for (var i = 0; i < 4; i++) {
        table_str += '<tr><td>Player' + String(i) + '</td><td>' + String(action_json["scores"][i]) + '</td></tr>';
    }
    table_str += '</table></div>';

    confirm_str = '<div class="end_kyoku_confirm"><a href="#" onclick="confirm_end_kyoku()">OK</a></div>';

    document.getElementById("end_kyoku_info").innerHTML = info_str + hora_str + tehai_str + table_str + confirm_str;
    document.getElementById("dialog_end_kyoku").style.display = "block";
}

function tehai_clicked(pos) {
    eel.tehai_clicked(pos);
}

function hora_clicked() {
    reset_button_ui_game();
    eel.do_hora();
}

function reach_clicked() {
    reset_button_ui_game();
    eel.do_reach();
}

function daiminkan_clicked() {
    reset_button_ui_game(); // 大明槓をしても他家がアガリをする場合など、その後の進行は不確定なため、はやいうちにbutton_uiはリセットする。
    eel.do_daiminkan();
}

function pass_clicked() {
    reset_button_ui_game();
    eel.do_pass();
}

function ryukyoku_clicked() {
    reset_button_ui_game();
    eel.do_kyushukyuhai();
}

function ankan_clicked(hai_str) {
    reset_button_ui_game();
    eel.do_ankan(hai_str);
}

function kakan_clicked(hai_str) {
    reset_button_ui_game();
    eel.do_kakan(hai_str);
}

function confirm_end_kyoku() {
    document.getElementById("dialog_end_kyoku").style.display = "none";
    eel.confirm_end_kyoku();
}