function fetchFriends(){
    $('#friendsDiv').html('');
    $.ajax({
        url: '/api/friends',
        type: "GET",
        contentType: "application/json",
        success: function (result) {
            if (result != null && result != "" && result != undefined && result.data != null && result.data.length > 0) {
                var users = { userf: result.data };
                $.get("/static/JQTemplates/friendsTbl.html", function(data, textStatus, XMLHttpRequest){
                    var markup = data;
                    /* Compile markup string as a named template */
                    $.template( "firTemp", markup );
                    /* Render the named template */
                    rendText = $.tmpl( "firTemp", users );
                    $('#friendsDiv').html(rendText.html());
                });
            } else{
                $('#friendsDiv').html('Add friend from Nav Bar');
            }
        },
        error: function () {
            $.notify("Some error occured. Try again later", "error");
        }
    });
}

function deleteFriend(friend_id){
    $.ajax({
        url: '/api/friend/' + friend_id,
        type: "DELETE",
        contentType: "application/json",
        success: function (result) {
            if (result != null && result != undefined) {
                if (result.data.success) {
                    fetchFriends();
                    $.notify(result.message, 'success');
                } else {
                    $.notify(result.message, 'error');
                }
            }
        },
        error: function () {
            $.notify("Some error occured. Try again later", "error");
        }
    });
}

function friendProfile(friend_id, override, show_all){
    if(override == null || override === 'undefined'){
        override = 0;
    }
    if(show_all == null || show_all === 'undefined'){
        show_all = 0;
    }
    $.ajax({
        url: '/api/submissions/' + friend_id + '/?refetchSubs=' + override + '&showAll=' + show_all +'&rand=' + Math.random() * 2909,
        type: "GET",
        contentType: "application/json",
        success: function (result) {
            if (result != null && result != "" && result != undefined && result.data != null && result.data.length > 0) {
                var submissions = { userf: result.data };
                $.get("/static/JQTemplates/friendProfileTbl.html", function(data, textStatus, XMLHttpRequest){
                    var markup = data;
                    /* Compile markup string as a named template */
                    $.template( "profileTemp", markup );
                    /* Render the named template */
                    rendText = $.tmpl( "profileTemp", submissions );
                    $('#profileDiv').html(rendText.html());
                });
            } else{
                $('#profileDiv').html('Your friend didn\'t make a submission since your last visit!');
            } 
        },
        error: function () {
            $.notify("Some error occured. Try again later", "error");
        }
    });
}

function addTODOList(problemCode, contestCode){
    postdata = {
        "problemCode" : problemCode,
        "contestCode" : contestCode,
    }
    $.ajax({
        url: '/api/mytodolist',
        type: "POST",
        data: JSON.stringify(postdata),
        contentType: "application/json",
        success: function (result) {
            $.notify(result.data, "success");
        },
        error: function () {
            $.notify("Some error occured. Try again later", "error");
        }
    });
}

function logVisit(friend_username){
    $.ajax({
        url: '/api/logvisit/' + friend_username + '/?rand=' + Math.random() * 1111,
        type: "PUT",
        contentType: "application/json",
        success: function (result) {
            console.log(result)
        },
        error: function (error) {
            console.log(error);
        }
    });
}