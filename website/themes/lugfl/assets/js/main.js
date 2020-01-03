
$(document).ready(function(){
	"use strict";

	var window_width 	 = $(window).width(),
	window_height 		 = window.innerHeight,
	header_height 		 = $(".default-header").height(),
	header_height_static = $(".site-header.static").outerHeight(),
	fitscreen 			 = window_height - header_height;
	$(".fullscreen").css("height", window_height)
	$(".fitscreen").css("height", fitscreen);
	$(".menu-bar").on('click touch', function(e){
		e.preventDefault();
		$(".navbar-nav").toggleClass('responsive');
		$("span", this).toggleClass("lnr-menu lnr-cross");
		$(".main-menu").addClass('mobile-menu');
	});
	$('.img-pop-up').magnificPopup({
		type: 'image',
		gallery:{enabled:true}
	});
});
