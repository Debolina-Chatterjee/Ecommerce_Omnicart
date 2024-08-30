const body = document.querySelector("body");
const darkLight = document.querySelector("#darkLight");
const sidebar = document.querySelector(".sidebar");
const submenuItems = document.querySelectorAll(".submenu_item");
const sidebarOpen = document.querySelector("#sidebarOpen");
const sidebarClose = document.querySelector(".collapse_sidebar");
const sidebarExpand = document.querySelector(".expand_sidebar");
setTimeout(function(){
sidebar.classList.add("close");
},1000)
sidebarOpen.addEventListener("click", () => sidebar.classList.toggle("close"));

sidebarClose.addEventListener("click", () => {
  sidebar.classList.add("close", "hoverable");
});
sidebarExpand.addEventListener("click", () => {
  sidebar.classList.remove("close", "hoverable");
});

sidebar.addEventListener("mouseenter", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.remove("close");
  }
});
sidebar.addEventListener("mouseleave", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.add("close");
  }
});

darkLight.addEventListener("click", () => {
  body.classList.toggle("dark");
  if (body.classList.contains("dark")) {
    document.setI
    darkLight.classList.replace("bx-sun", "bx-moon");
  } else {
    darkLight.classList.replace("bx-moon", "bx-sun");
  }
});

submenuItems.forEach((item, index) => {
  item.addEventListener("click", () => {
    item.classList.toggle("show_submenu");
    submenuItems.forEach((item2, index2) => {
      if (index !== index2) {
        item2.classList.remove("show_submenu");
      }
    });
  });
});

if (window.innerWidth < 768) {
  sidebar.classList.add("close");
} else {
  sidebar.classList.remove("close");
}

// Product Delete
function product_delete() {
  $(".delete-product").on("click", function(e) {
    e.preventDefault();

    // Get the product ID from the data attribute
    var productId = $(this).data("product-id");
    var token = $(this).attr('token');
    // Confirm deletion
    if (confirm("Are you sure you want to delete this product?")) {
      // Send AJAX request to delete the product
      $.ajax({
        url: "/product/delete/" + productId + "/",  // Replace with your actual URL
        method: "POST",
        data: {
          csrfmiddlewaretoken: token,
          // Other data you may want to send
        },
        success: function(response) {
          // Handle success, e.g., remove the deleted product from the table
          alert("Product deleted successfully!");
          location.reload();  // Reload the page or update the table
        },
        error: function(error) {
          alert("Error deleting product. Please try again.");
        }
      });
    }
  });
};
setTimeout(function(){
  product_delete()
},1000);