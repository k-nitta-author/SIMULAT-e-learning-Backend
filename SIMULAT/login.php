<?php
// Function to sanitize user input
function sanitizeInput($data) {
    return htmlspecialchars(stripslashes(trim($data)));
}

// Include the database connection logic
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "simulatdb";

$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check if the user is already logged in, redirect to the information page if true
session_start();
if (isset($_SESSION['token_id'])) {
    header("Location: information.php");
    exit();
}

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Sanitize input data
    $tokenID = sanitizeInput($_POST["token_id"]);

    // Check if the token ID exists in the database using a prepared statement
    $stmt = $conn->prepare("SELECT * FROM Student WHERE token_id = ?");
    $stmt->bind_param("s", $tokenID);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result && $result->num_rows > 0) {
        // Token ID exists, set session variable and redirect to information page
        $_SESSION['token_id'] = $tokenID;
        header("Location: information.php");
        exit();
    } else {
        // Token ID not found, display error message
        $loginError = "Invalid Token ID. Please try again.";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <?php
    if (isset($loginError)) {
        echo "<p style='color: red;'>$loginError</p>";
    }
    ?>
    <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
        <label for="token_id">Token ID:</label>
        <input type="text" name="token_id" required>
        <br>
        <input type="submit" value="Login">
    </form>
    
    <p>Don't have an account? <a href="registration.php">Register here</a>.</p>
</body>
</html>