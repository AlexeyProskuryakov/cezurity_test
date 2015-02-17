function form_label(nodeObject){
	nodeObject.label = nodeObject.label + ' ('+nodeObject.level+')';
	return nodeObject;
}
//initing tree
var t = $("#tree").tree({data:[{label:'#',id:-1}]});
t.bind('tree.dblclick',
	function(event) {
		console.log(event.node);
		$.ajax({
			url:'/children',
			type:'GET',
			data:{id:event.node.id}
		}).done(function(data){
			console.log(data);
			if (data.ok){						
				for (var i=0;i<data.result.length;i++){		        		
					var nodeObject = data.result[i];
					var new_node = t.tree('getNodeById', nodeObject.id);
					if (new_node==undefined){
						t.tree('appendNode', form_label(nodeObject), event.node);
					}
				}
			}
			t.tree('openNode',event.node);
		});

	});

//adding results for tree
function add_result_to_tree(tree, result){
	tree.tree('reload');
	var selected = [];
	for (var path_id=0; path_id<result.length; path_id++){
		var path = result[path_id];
		console.log('path:',path);

		var root_node_object = path[path.length-1];
		var root_node = tree.tree('getNodeById', root_node_object.id);
		if (root_node == undefined){
			root = tree.tree('getNodeById', -1);
			root_node = tree.tree('appendNode', form_label(root_node_object), root);
			tree.tree('openNode',root);
		}
		console.log('root node:', root_node);
		for (var i=path.length-2; i>=0; i--){
			console.log('appending node', path[i], 'for node', root_node);
			var new_node = tree.tree('getNodeById', path[i].id)
			if (new_node == undefined){
				new_node = tree.tree('appendNode', form_label(path[i]), root_node);	
			}
			tree.tree('openNode', root_node);
			root_node = new_node;
		}
		selected.push(root_node.id);
	}
	tree.tree('setState',{selected_node:selected});
};

function search_by_level(){
	var level = $('#level').val();
	$.ajax({
		url:'/level',
		type:'POST',
		data:{level:level}
	}).done(function(data){
		if (data.ok){
			var result = data.result;
			console.log('result: ', result);
			add_result_to_tree(t,result);
			
		}
	});
};

function search_by_label(){
	var label = $('#label').val();
	console.log('wil search:', label);
	$.ajax({
		url:'/label',
		type:'POST',
		data:{label:label}
	}).done(function(data){
		if (data.ok){
			var result = data.result;
			console.log('result: ', result);
			add_result_to_tree(t,result);
			
		}
	});
};

//some context menu functions
var menu = $('#rmenu');

function closeMenu(){
	menu.toggleClass('hide');
	menu.toggleClass("show");  
};

function edit_node(){
	var new_label = $('#edit_accum').val();
	var node_id = $('#id_accum').val();
	if (new_label.length>0){
		$.ajax({
			url:'/manage_element',
			type:'POST',
			data:{new_label:new_label, id:node_id}
		}).done(function(data){
			var node = t.tree('getNodeById', node_id);
			var new_node_content = form_label({'label':new_label, 'level':node.level});
			t.tree('updateNode', node, new_node_content);
		});
	}
};
function delete_node(){
	var node_id = $('#id_accum').val();
	$.ajax({
		url:'/manage_element',
		type:'DELETE',
		data:{id:node_id}
	}).done(function(data){
		var node = t.tree('getNodeById', node_id);
		t.tree('removeNode',node);
	})
};

t.bind('tree.contextmenu', function(event){
	$('#node_represenet').text(event.node.name);
	$('#id_accum').val(event.node.id);
	menu.toggleClass('hide');
	menu.toggleClass("show");  
	menu.css('top',mouseY(event));
	menu.css('left',mouseX(event));
});


function mouseX(evt) {
	if (evt.pageX) {
		return evt.pageX;
	} else if (evt.clientX) {
		return evt.clientX + (document.documentElement.scrollLeft ?
			document.documentElement.scrollLeft :
			document.body.scrollLeft);
	} else {
		return null;
	}
}

function mouseY(evt) {
	if (evt.pageY) {
		return evt.pageY;
	} else if (evt.clientY) {
		return evt.clientY + (document.documentElement.scrollTop ?
			document.documentElement.scrollTop :
			document.body.scrollTop);
	} else {
		return null;
	}
}