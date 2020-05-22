//Set up and mapping with Vue
let processProducts = function () {
    let index = 0;
    app.products.map((product) => {
        Vue.set(product, 'index', index++);
        Vue.set(product, 'showReviews', false);
        Vue.set(product, 'otherReviews', []);
        Vue.set(product, 'show', true);
        Vue.set(product, 'yourReview', { rating: 0, numStars: 0, body: '' });
    });
};

//Used to retrieve all products in the database for the index page
let getAllProducts = function() {
    $.getJSON(getAllProductsUrl, function(response) {
        app.products = response.products;
        processProducts();
        console.log(app.products);
    });
};

//To see who is logged into the application and it is also used to exit other functions such as getYourReview if no one is logged in
let getLoggedInUser = function(callback) {
    $.getJSON(getLoggedInUserUrl, function(response) {
        app.loggedInUser = response.user;
        callback();
    });
};

//Used to find specific products by name with the search bar on the index page
let doSearch = function () {
    for (let i = 0; i < app.products.length; i++) {
        let product = app.products[i];
        if (product.product_name.toUpperCase().startsWith(app.searchBar.toUpperCase()) || app.searchBar == '') {
            product.show = true;
        } else {
            product.show = false;
        }
    }
}

//This is called when a page is started or refreshed to load up the contents
let onPageLoad = function() {
    getLoggedInUser(function() {
        getAllProducts();
    });
};

//This is to retrieve the review that the logged in user has already in the database
let getYourReview = function(productIndex) {
    if (app.loggedInUser == undefined) {
        return;
    }

    let product = app.products[productIndex];

    $.getJSON(getYourReviewUrl, { product_id: product.id, email: app.loggedInUser }, function(response) {
        if (response.review != null) {
            product.yourReview.rating = response.review.rating;
            product.yourReview.numStars = response.review.rating;
            product.yourReview.body = response.review.body;
        }
    });
};

//Used to close the reviews with a close button 
let closeReviews = function (productIndex) {
    let product = app.products[productIndex];
    product.showReviews = false;
}
//This is to retrieve all the reviews that was not completed by the logged in user
let getOtherReviews = function(productIndex) {
    let product = app.products[productIndex];
    $.getJSON(getOtherReviewsUrl, { product_id: product.id }, function(response) {
        product.otherReviews = response.other_reviews;
    });
};

//Used on the index page for the Review buttons to display reviews for each product
let toggleReviewsSection = function(productIndex) {
    let product = app.products[productIndex];
    for (let i = 0; i < app.products.length; i++) {
        if (i != productIndex) {
            app.products[i].showReviews = false;
        }
    }
    product.showReviews = !product.showReviews;
};

//Fills in stars up to where the mouse is pointed at from 1-5 stars
let hoverStar = function(productIndex, starNum) {
    let product = app.products[productIndex];
    product.yourReview.numStars = starNum;
};

//This display's the star rating
let leaveStarRow = function(productIndex) {
    let product = app.products[productIndex];
    product.yourReview.numStars = product.yourReview.rating;
};

//Saves the review input from the user into the database
let saveReview = function(productIndex) {
    if (app.loggedInUser == undefined) {
        return;
    }

    let product = app.products[productIndex];
    let yourReview = product.yourReview;
    Vue.set(yourReview, 'hasBeenSaved', false);

    $.post(saveReviewUrl, {
        product_id: product.id,
        email: app.loggedInUser,
        body: yourReview.body
    }, function(response) {
        yourReview.hasBeenSaved = true;
        setTimeout(function() {
            yourReview.hasBeenSaved = false;
        }, 1000);
    });
};

//This sets the star rating and inputs that into the database
let clickStar = function(productIndex, starNum) {
    let product = app.products[productIndex];
    product.yourReview.rating = starNum;
    $.post(updateStarUrl, {
        product_id: product.id,
        email: app.loggedInUser,
        rating: starNum
    }, function() {
        let sum = 0
        let length = product.otherReviews.length + 1;
        for (let i = 0; i < product.otherReviews.length; i++) {
            if (product.otherReviews[i].rating == 0) {
                length--;
            } else {
                sum += product.otherReviews[i].rating;
            }
        }
        if (product.yourReview.rating == 0) {
            length --;
        } else {
            sum += product.yourReview.rating;
        }
        product.avg_rating = sum / length;
    });
};

//Used to set up the contents of the index page
let app = new Vue({
    el: "#app",
    delimiters: ['${', '}'],
    unsafeDelimiters: ['!{', '}'],
    data: {
        products: [],
        starIndices: [1, 2, 3, 4, 5],
        loggedInUser: undefined,
        searchBar: ''
    },
    methods: {
        getYourReview: getYourReview,
        getOtherReviews: getOtherReviews,
        toggleReviewsSection: toggleReviewsSection,
        saveReview: saveReview,
        hoverStar: hoverStar,
        leaveStarRow: leaveStarRow,
        clickStar: clickStar,
        doSearch: doSearch
    }
});

onPageLoad();