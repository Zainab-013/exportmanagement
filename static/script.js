$(document).ready(function() {
    $(".dropdown").hover(
        function() {
            $(this).find(".dropdown-content").slideDown(200);
        },
        function() {
            $(this).find(".dropdown-content").slideUp(200);
        }
    );
});

function fetchProduct() {
    let productId = document.getElementById("product_id").value;
    if (!productId) {
        alert("Please enter a Product ID!");
        return;
    }

    fetch(`/product/${productId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("product_details").innerHTML = "Product not found!";
            } else {
                document.getElementById("product_details").innerHTML =
                    `<p>Name: ${data.name}</p>
                     <p>Category: ${data.category}</p>
                     <p>Price: ₹${data.price}</p>
                     <p>Export States: ${data.export_states}</p>`;
            }
        })
        .catch(error => console.error("Error:", error));
}
