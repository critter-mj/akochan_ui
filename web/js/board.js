function hai_img_tag_ang(hai_str, ang) {
    var type = (ang == 1 ? 'repeated laid-pai' : 'repeated pai');
    return '<img class="' + type + '" style="display: inline;" src="img/' + hai_str + '_' + String(ang) + '.png">';
}

function hai_img_tag(hai_str) {
    return hai_img_tag_ang(hai_str, 0);
}

function hailist_img_tag(hai_list) {
    var ret = '';
    for (var i = 0; i < hai_list.length; i++) {
        ret += hai_img_tag(hai_list[i]);
    }
    return ret;
}

function dump_player_info(ps) {
    var ret = '<div class="player-info-container">';
    ret += '<div class="onboard_string">' + ps["name"] + '</div>';
    ret += '<img class="wind_icon" style="display: inline;" src="img/Wind_' + ps["jikaze"] + '.png">';
    ret += '<span class="onboard_string">  ' + ps["score"] + '  </span>';
    if (ps["reach_accepted"]) {
        ret += '<img class="reach_stick" style="display: inline;" src="img/Reach.png">';
    }
    ret += '</div>';
    return ret;
}

function dump_tehai(ps) {
    var ret = '<div class="tehai-container pai-row">\n';
    ret += '<img class="repeated">' + hailist_img_tag(ps["tehai"]) + '\n';
    if ("current_tsumo" in ps) {
        ret += '<img class="tsumo-pai pai" style="display: inline;" src="img/' + ps["current_tsumo"] + '_0.png">';
    } else {
        ret += '<img class="tsumo-pai" style="display: none;">';
    }
    for (var i = 0; i < 13 - ps["tehai"].length; i++) {
        ret += '<img class="tsumo-pai" style="display: none;">';
    }
    ret += '\n</div>\n';
    return ret;
}

function dump_kawa(kawa) {
    var hai_list = [[], [], []];
    var ang_list = [[], [], []];
    var cnt = 0;
    for (var i = 0; i < kawa.length; i++) {
        if (!kawa[i]["is_taken"]) {
            var dan = Math.floor(cnt/6);
            if (2 < dan) { dan = 2; }
            hai_list[dan].push(kawa[i]["pai"]);
            ang_list[dan].push(kawa[i]["is_reach"] ? 1 : 0);
            cnt++;
        } 
    }
    var ret = '<div class="ho">\n';
    ret += '<div class="repeated pai-row">\n';
    ret += '<img class="repeated">\n';
    ret += '</div>\n';
    for (var i = 0; i < 3; i++) {
        ret += '<div class="repeated pai-row" style="display: block;">\n';
        ret += '<img class="repeated">';
        for (var j = 0; j < hai_list[i].length; j++) {
            ret += hai_img_tag_ang(hai_list[i][j], ang_list[i][j]);
        }
        // repeated pai-rowの子要素数をゲームの進行度合いに寄らず固定にしておくと、更新の時に速度面で都合が良い。3段目は6を超える可能性があるので大きめ(10)にする。
        for (var j = hai_list[i].length; j < 10; j++) {
            ret += '<img class="repeated pai" style="display: none;">';
        }
        ret += '\n</div>\n';
    }
    ret += '</div>\n';
    return ret;
}

function dump_chi_pon(fuuro_elem) {
    var ret = '<span class="repeated" style="display: inline;">\n';
    ret += '<img class="repeated">';
    if (fuuro_elem["target_relative"] == 1) {
        ret += hai_img_tag(fuuro_elem["consumed"][0]) + hai_img_tag(fuuro_elem["consumed"][1]) + hai_img_tag_ang(fuuro_elem["pai"], 1);
    } else if (fuuro_elem["target_relative"] == 2) {
        ret += hai_img_tag(fuuro_elem["consumed"][0]) + hai_img_tag_ang(fuuro_elem["pai"], 1) + hai_img_tag(fuuro_elem["consumed"][1]);
    } else if (fuuro_elem["target_relative"] == 3) {
        ret += hai_img_tag_ang(fuuro_elem["pai"], 1) + hai_img_tag(fuuro_elem["consumed"][0]) + hai_img_tag(fuuro_elem["consumed"][1]);
    }
    ret += '\n</span>\n';
    return ret;
}

function dump_minkan(fuuro_elem) {
    var ret = '<span class="repeated" style="display: inline;">\n';
    ret += '<img class="repeated">';
    if (fuuro_elem["target_relative"] == 1) {
        ret += hai_img_tag(fuuro_elem["consumed"][0]) + hai_img_tag(fuuro_elem["consumed"][1]) + hai_img_tag(fuuro_elem["consumed"][2]) + hai_img_tag_ang(fuuro_elem["pai"], 1);
    } else if (fuuro_elem["target_relative"] == 2) {
        ret += hai_img_tag(fuuro_elem["consumed"][0]) + hai_img_tag_ang(fuuro_elem["pai"], 1) + hai_img_tag(fuuro_elem["consumed"][1]) + hai_img_tag(fuuro_elem["consumed"][2]);
    } else if (fuuro_elem["target_relative"] == 3) {
        ret += hai_img_tag_ang(fuuro_elem["pai"], 1) + hai_img_tag(fuuro_elem["consumed"][0]) + hai_img_tag(fuuro_elem["consumed"][1]) + hai_img_tag(fuuro_elem["consumed"][2]);
    }
    ret += '\n</span>\n';
    return ret;
}

function dump_ankan(fuuro_elem) {
    var ret = '<span class="repeated" style="display: inline;">\n';
    ret += '<img class="repeated">';
    ret += hai_img_tag('0') + hai_img_tag(fuuro_elem["consumed"][0]) + hai_img_tag(fuuro_elem["consumed"][3]) + hai_img_tag('0');
    return ret;
}

function dump_fuuro(fuuro) {
    var ret = '<div class="furo-container pai-row">\n';
    ret += '<span class="repeated">\n';
    ret += '<img class="repeated">\n';
    ret += '</span>\n';
    for (var i = fuuro.length - 1; 0 <= i; i--) {
        if (fuuro[i]["type"] == "chi" || fuuro[i]["type"] == "pon") {
            ret += dump_chi_pon(fuuro[i]);
        } else if (fuuro[i]["type"] == "daiminkan" || fuuro[i]["type"] == "kakan") {
            ret += dump_minkan(fuuro[i]);
        } else if (fuuro[i]["type"] == "ankan") {
            ret += dump_ankan(fuuro[i]);
        }
    }
    ret += '</div>\n';
    return ret;
}

function dump_player(ps, pid) {
    var ret = '<div class="repeated player player-' + pid + '" style="display: block;">\n';
    ret += dump_player_info(ps);
    ret += dump_kawa(ps["kawa"]);
    ret += dump_tehai(ps);
    ret += dump_fuuro(ps["fuuro"]);
    ret += '</div>\n';
    ret += '<div class="player-footer"></div>\n';
    return ret;
}

function dump_kyoku_info(json) {
    var ret = '<div class="kyoku-info-container"><span class="onboard_string">';
    if (json["bakaze"] == 'E') {
        ret += '東';
    } else if (json["bakaze"] == 'S') {
        ret += '南';
    } else if (json["bakaze"] == 'W') {
        ret += '西';
    } else if (json["bakaze"] == 'N') {
        ret += '北';
    }
    ret += ' ' + String(json["kyoku"]) + ' 局 ' + String(json["honba"]) + ' 本場';
    ret += '</span></div>';
    return ret; 
}

function dump_wanpai() {
    var ret = '<div class="wanpais-container">\n';
    ret += '</div>\n';
    return ret;  
}

function dump_num_info(json) {
    var ret = '<div class="num_info-container">\n';
    ret += '<img class="kyotaku" style="display: inline;" src="img/Reach.png">';
    ret += '<span class="onboard_string">×  ' + String(json["kyotaku"]) + '  </span>'
    ret += '<img class="remain_icon" style="display: inline;" src="img/0_0.png">';
    ret += '<span class="onboard_string">×  ' + String(70 - json["total_tsumo_num"]) + '</span>'
    ret += '</div>\n';
    return ret;
}

function dump_board(json, view_pid) {
    ret = '';
    for (var pid = 0; pid < 4; pid++) {
        ret += dump_player(json["player_state"][(view_pid + pid) % 4], pid);
    }
    ret += dump_kyoku_info(json);
    ret += dump_num_info(json);
    return ret;
}

function update_board(state_json, view_pid) {
    if (document.getElementById("board").innerHTML == "") {
        document.getElementById("board").innerHTML = dump_board(state_json, view_pid);
    } else {
        board_new = dump_board(state_json, view_pid);
        var doc_new = new DOMParser().parseFromString(board_new, "text/html");

        let tehais_old = document.getElementsByClassName("tehai-container pai-row");
        let tehais_new = doc_new.getElementsByClassName("tehai-container pai-row");
        for (var i = 0; i < tehais_old.length; i++) {
            for (var j = 0; j < tehais_old[i].children.length; j++) {
                if (tehais_old[i].children[j].outerHTML != tehais_new[i].children[j].outerHTML) {
                    tehais_old[i].children[j].outerHTML = tehais_new[i].children[j].outerHTML;
                }
            }
        }

        let kawas_old = document.getElementsByClassName("repeated pai-row");
        let kawas_new = doc_new.getElementsByClassName("repeated pai-row");
        for (var i = 0; i < kawas_old.length; i++) {
            for (var j = 0; j < kawas_old[i].children.length; j++) {
                if (kawas_old[i].children[j].outerHTML != kawas_new[i].children[j].outerHTML) {
                    kawas_old[i].children[j].outerHTML = kawas_new[i].children[j].outerHTML;
                }
            }
        }

        let furos_old = document.getElementsByClassName("furo-container pai-row");
        let furos_new = doc_new.getElementsByClassName("furo-container pai-row");
        for (var i = 0; i < furos_old.length; i++) {
            if (furos_old[i].innerHTML != furos_new[i].innerHTML) {
                furos_old[i].innerHTML = furos_new[i].innerHTML;
            }
        }

        let player_info_old = document.getElementsByClassName("player-info-container");
        let player_info_new = doc_new.getElementsByClassName("player-info-container");
        for (var i = 0; i < player_info_old.length; i++) {
            if (player_info_old[i].innerHTML != player_info_new[i].innerHTML) {
                player_info_old[i].innerHTML = player_info_new[i].innerHTML;
            }
        }

        let kyoku_info_old = document.getElementsByClassName("kyoku-info-container")[0];
        let kyoku_info_new = doc_new.getElementsByClassName("kyoku-info-container")[0];
        if (kyoku_info_old.innerHTML != kyoku_info_new.innerHTML) {
            kyoku_info_old.innerHTML = kyoku_info_new.innerHTML;
        }

        let wanpai_old = document.getElementsByClassName("wanpais-container")[0];
        let wanpai_new = doc_new.getElementsByClassName("wanpais-container")[0];
        for (var i = 0; i < wanpai_old.children.length; i++) {
            if (wanpai_old.children[i].outerHTML != wanpai_new.children[i].outerHTML) {
                wanpai_old.children[i].outerHTML = wanpai_new.children[i].outerHTML;
            }
        }

        if (wanpai_old.innerHTML != wanpai_new.innerHTML) {
            wanpai_old.innerHTML = wanpai_new.innerHTML;
        }

        let num_info_old = document.getElementsByClassName("num_info-container")[0];
        let num_info_new = doc_new.getElementsByClassName("num_info-container")[0];
        for (var i = 0; i < num_info_old.children.length; i++) {
            if (num_info_old.children[i].outerHTML != num_info_new.children[i].outerHTML) {
                num_info_old.children[i].outerHTML = num_info_new.children[i].outerHTML;
            }
        }
    }
}