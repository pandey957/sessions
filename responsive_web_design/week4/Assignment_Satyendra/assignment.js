var albums_template, photos_template, photo_template;
var current_album = animals_data.category[0];
var current_photo = current_album.animals[0];
function showTemplate(template, data){
	var html = template(data);
	$('#content').html(html);
}
$(document).ready(function(){
	var source   = $("#albums-template").html();
	albums_template = Handlebars.compile(source);
	source   = $("#photos-template").html();
	photos_template = Handlebars.compile(source);
	source   = $("#photo-template").html();
	photo_template = Handlebars.compile(source);
	source   = $("#about-template").html();
	about_template = Handlebars.compile(source);
	$("#albums-tab").click(function () {
		showTemplate(albums_template, animals_data);
		$(".nav-tabs .active").removeClass("active");
		$("#li-albums-tab").addClass("active");
		$(".album-thumbnail").click(function (){
			var index = $(this).data("id");
			current_album = animals_data.category[index];
			showTemplate(photos_template, current_album);
			$(".nav-tabs .active").removeClass("active");
			$("#li-photos-tab").addClass("active");
			$(".photo-thumbnail").click(function (){
				var index = $(this).data("id");
				$(".nav-tabs .active").removeClass("active");
			    $("#li-photo-tab").addClass("active");
				current_photo = current_album.animals[index];
				showTemplate(photo_template, current_photo);
			});
		});		
	});

	$("#photos-tab").click(function () {
		showTemplate(photos_template, current_album);
		$(".nav-tabs .active").removeClass("active");
		$("#li-photos-tab").addClass("active");
		$(".photo-thumbnail").click(function (){
			var index = $(this).data("id");
			current_photo = current_album.animals[index];
			showTemplate(photo_template, current_photo);
		});
	});

	$("#photo-tab").click(function () {
		showTemplate(photo_template, current_photo);
		$(".nav-tabs .active").removeClass("active");
		$("#li-photo-tab").addClass("active");
		});
	$("#about-tab").click(function(){
		showTemplate(about_template,current_photo);
		$(".nav-tabs .active").removeClass("active");
		$("#li-about-tab").addClass("active");
	});

	$("#about-tab").click();
});
