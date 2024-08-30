
/*=======================================
[Start Activation Code]
=========================================
	01. Mobile Menu JS
	02. Sticky Header JS
	03. Search JS
	04. Slider Range JS
	05. Home Slider JS
	06. Popular Slider JS
	07. Quick View Slider JS
	08. Home Slider 4 JS
	09. CountDown
	10. Flex Slider JS
	11. Cart Plus Minus Button
	12. Checkbox JS
	13. Extra Scroll JS
	14. Product page Quantity Counter
	15. Video Popup JS
	16. Scroll UP JS
	17. Nice Select JS
	18. Others JS
	19. Preloader JS
=========================================
[End Activation Code]
=========================================*/ 
(function($) {
    "use strict";
     $(document).on('ready', function() {	
      
		/*====================================
			Mobile Menu
		======================================*/ 	
		$('.menu').slicknav({
			prependTo:".mobile-nav",
			duration:300,
			animateIn: 'fadeIn',
			animateOut: 'fadeOut',
			closeOnClick:true,
		});
		
		/*====================================
		03. Sticky Header JS
		======================================*/ 
		jQuery(window).on('scroll', function() {
			if ($(this).scrollTop() > 200) {
				$('.header').addClass("sticky");
			} else {
				$('.header').removeClass("sticky");
			}
		});
		
		/*=======================
		  Search JS JS
		=========================*/ 
		$('.top-search a').on( "click", function(){
			$('.search-top').toggleClass('active');
		});
		
		/*=======================
		  Slider Range JS
		=========================*/ 
		$( function() {
			$( "#slider-range" ).slider({
			  range: true,
			  min: 0,
			  max: 500,
			  values: [ 120, 250 ],
			  slide: function( event, ui ) {
				$( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
			  }
			});
			$( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
			  " - $" + $( "#slider-range" ).slider( "values", 1 ) );
		} );
		
		/*=======================
		  Home Slider JS
		=========================*/ 
		$('.home-slider').owlCarousel({
			items:1,
			autoplay:true,
			autoplayTimeout:5000,
			smartSpeed: 400,
			animateIn: 'fadeIn',
			animateOut: 'fadeOut',
			autoplayHoverPause:true,
			loop:true,
			nav:true,
			merge:true,
			dots:false,
			navText: ['<i class="ti-angle-left"></i>', '<i class="ti-angle-right"></i>'],
			responsive:{
				0: {
					items:1,
				},
				300: {
					items:1,
				},
				480: {
					items:2,
				},
				768: {
					items:3,
				},
				1170: {
					items:4,
				},
			}
		});
		
		
	
	
		/*=======================
		  Popular Slider JS
		=========================*/ 
		$('.popular-slider').owlCarousel({
			items:1,
			autoplay:true,
			autoplayTimeout:5000,
			smartSpeed: 400,
			animateIn: 'fadeIn',
			animateOut: 'fadeOut',
			autoplayHoverPause:true,
			loop:true,
			nav:true,
			merge:true,
			dots:false,
			navText: ['<i class="ti-angle-left"></i>', '<i class="ti-angle-right"></i>'],
			responsive:{
				0: {
					items:1,
				},
				300: {
					items:1,
				},
				480: {
					items:2,
				},
				768: {
					items:3,
				},
				1170: {
					items:4,
				},
			}
		});
		
		/*===========================
		  Quick View Slider JS
		=============================*/ 
		$('.quickview-slider-active').owlCarousel({
			items:1,
			autoplay:true,
			autoplayTimeout:5000,
			smartSpeed: 400,
			autoplayHoverPause:true,
			nav:true,
			loop:true,
			merge:true,
			dots:false,
			navText: ['<i class=" ti-arrow-left"></i>', '<i class=" ti-arrow-right"></i>'],
		});
		
		/*===========================
		  Home Slider 4 JS
		=============================*/ 
		$('.home-slider-4').owlCarousel({
			items:1,
			autoplay:true,
			autoplayTimeout:5000,
			smartSpeed: 400,
			autoplayHoverPause:true,
			nav:true,
			loop:true,
			merge:true,
			dots:false,
			navText: ['<i class=" ti-arrow-left"></i>', '<i class=" ti-arrow-right"></i>'],
		});
		
		/*====================================
		14. CountDown
		======================================*/ 
		$('[data-countdown]').each(function() {
			var $this = $(this),
				finalDate = $(this).data('countdown');
			$this.countdown(finalDate, function(event) {
				$this.html(event.strftime(
					'<div class="cdown"><span class="days"><strong>%-D</strong><p>Days.</p></span></div><div class="cdown"><span class="hour"><strong> %-H</strong><p>Hours.</p></span></div> <div class="cdown"><span class="minutes"><strong>%M</strong> <p>MINUTES.</p></span></div><div class="cdown"><span class="second"><strong> %S</strong><p>SECONDS.</p></span></div>'
				));
			});
		});
		
		/*====================================
		16. Flex Slider JS
		======================================*/
		(function($) {
			'use strict';	
				$('.flexslider-thumbnails').flexslider({
					animation: "slide",
					controlNav: "thumbnails",
				});
		})(jQuery);
		
		/*====================================
		  Cart Plus Minus Button
		======================================*/
	
			// Plus button click
			$('.plus button').on('click', function () {
			  var itemId = $(this).data('item-id');
			  var currentQuantity = parseInt($('input[name="quant[' + itemId + ']"]').val());
			  var newQuantity = currentQuantity + 1;
		
			  updateCartItemQuantity(itemId, newQuantity);
			});
		
			// Minus button click
			$('.minus button').on('click', function () {
			  var itemId = $(this).data('item-id');
			  var currentQuantity = parseInt($('input[name="quant[' + itemId + ']"]').val());
			  var newQuantity = Math.max(currentQuantity - 1, 1);
		
			  updateCartItemQuantity(itemId, newQuantity);
			});
		
			function updateCartItemQuantity(itemId, newQuantity) {
			  // Make AJAX request to update quantity
			  $.ajax({
				url: '/update-cart-quantity/' + itemId + '/' + newQuantity + '/',
				type: 'GET',
				success: function (data) {
				  if (data.success) {
					// Update the input field value on success
					$('input[name="quant[' + itemId + ']"]').val(newQuantity);
					location.reload(true);
				
				  } else {
					console.error('Failed to update cart quantity:', data.message);
				  }
				},
				error: function () {
				  console.error('Failed to update cart quantity. Server error.');
				}
			  });
			}
		 

			$('.remove-item').on('click', function(e) {
				e.preventDefault();
				
				var itemId = $(this).data('item-id');
				
				$.ajax({
					url: '/remove-cart-item/' + itemId + '/',
					type: 'GET',
					success: function(data) {
						if (data.success) {
							// Use SweetAlert to show a success message
							Swal.fire({
								icon: 'success',
								title: 'Cart item removed successfully',
								showConfirmButton: false,
								timer: 1500 // Close the alert after 1.5 seconds
							}).then((result) => {
								/* Read more about isConfirmed, isDenied below */
								location.reload(true);
							});
				
							// Optionally, you can update the cart UI here without reloading the page
							// For example, you can remove the corresponding row from the table
				
							// Example: remove the table row containing the removed item
						
						} else {
							// Use SweetAlert to show an error message
							Swal.fire({
								icon: 'error',
								title: 'Failed to remove cart item',
								text: data.message
							});
						}
					},
					error: function() {
						// Use SweetAlert to show a server error message
						Swal.fire({
							icon: 'error',
							title: 'Failed to remove cart item',
							text: 'Server error'
						});
					}
				});
			});	
		/*=======================
		  Extra Scroll JS
		=========================*/
		$('.scroll').on("click", function (e) {
			var anchor = $(this);
				$('html, body').stop().animate({
					scrollTop: $(anchor.attr('href')).offset().top - 0
				}, 900);
			e.preventDefault();
		});
		
		/*===============================
		10. Checkbox JS
		=================================*/  
		$('input[type="checkbox"]').change(function(){
			if($(this).is(':checked')){
				$(this).parent("label").addClass("checked");
			} else {
				$(this).parent("label").removeClass("checked");
			}
		});
		
		/*==================================
		 12. Product page Quantity Counter
		 ===================================*/
		// $('.qty-box .quantity-right-plus').on('click', function () {
		// 	var $qty = $('.qty-box .input-number');
		// 	var currentVal = parseInt($qty.val(), 10);
		// 	if (!isNaN(currentVal)) {
		// 		$qty.val(currentVal + 1);
		// 	}
		// });
		// $('.qty-box .quantity-left-minus').on('click', function () {
		// 	var $qty = $('.qty-box .input-number');
		// 	var currentVal = parseInt($qty.val(), 10);
		// 	if (!isNaN(currentVal) && currentVal > 1) {
		// 		$qty.val(currentVal - 1);
		// 	}
		// });
		
		/*=====================================
		15.  Video Popup JS
		======================================*/ 
		$('.video-popup').magnificPopup({
			type: 'iframe',
			removalDelay: 300,
			mainClass: 'mfp-fade'
		});
		
		/*====================================
			Scroll Up JS
		======================================*/
		$.scrollUp({
			scrollText: '<span><i class="fa fa-angle-up"></i></span>',
			easingType: 'easeInOutExpo',
			scrollSpeed: 900,
			animation: 'fade'
		});  
		
	});
	
	/*====================================
	18. Nice Select JS
	======================================*/	
	$('select').niceSelect();
		
	/*=====================================
	 Others JS
	======================================*/ 	
	$( function() {
		$( "#slider-range" ).slider({
			range: true,
			min: 0,
			max: 500,
			values: [ 0, 500 ],
			slide: function( event, ui ) {
				$( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
			}
		});
		$( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
		  " - $" + $( "#slider-range" ).slider( "values", 1 ) );
	} );
	
	/*=====================================
	  Preloader JS
	======================================*/ 	
	//After 2s preloader is fadeOut
	$('.preloader').delay(2000).fadeOut('slow');
	setTimeout(function() {
	//After 2s, the no-scroll class of the body will be removed
	$('body').removeClass('no-scroll');
	}, 2000); //Here you can change preloader time
	 
	
/*=====================================
	  Category JS
	======================================*/ 	

	
		// Make AJAX request to fetch categories
		$.ajax({
			url: '/get-categories/',  // URL to your Django view for fetching categories
			type: 'GET',
			success: function(response) {
				// Handle success response
				var categories = response;
				console.log('Categories:', categories);
				
				// Clear existing options
				$('.nice-select ul.list').empty();
				
				// Update the dropdown list with fetched categories
				categories.forEach(function(category) {
					console.log('Category:', category);
					var listItem = $('<li>').attr('data-value', category.id).addClass('option');
					var categoryLink = $('<a>').attr('href', '/category/' + category.id + '/').text(category.name);
					categoryLink.appendTo(listItem);
					listItem.appendTo('.nice-select ul.list');
				});
			},
			error: function(xhr, status, error) {
				// Handle error response
				console.error('Error fetching categories:', error);
			}
		});

	

		/*=====================================
	  Tags JS
	======================================*/ 	


	$.ajax({
		url: '/get-tags/',  
		type: 'GET',
		success: function(response) {
			
			var tags = response; 
			
			console.log('Tags:', tags);
			// Clear existing options
			$('.all-category ul.main-category').empty();
			// Update the list with fetched tags
			tags.forEach(function(tag) {
				console.log('Tag:', tag.name); // Debugging: Check tag
				var listItem = $('<li>');
				var tagLink = $('<a>').attr('href', '/tags/' + tag.id + '/').text(tag.name);
				tagLink.appendTo(listItem);
				listItem.appendTo('.all-category ul.main-category');
			});
		},
		error: function(xhr, status, error) {
			// Handle error response
			console.error('Error fetching tags:', error);
		}
	});



	const toggles = document.querySelectorAll('.faq-toggle')

toggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
        toggle.parentNode.classList.toggle('active')
    })
})

})(jQuery);




