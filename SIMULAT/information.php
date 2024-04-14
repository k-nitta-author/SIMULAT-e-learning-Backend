<?php
// Start the session
session_start();

// Check if the user is logged in, redirect to login page if not
if (!isset($_SESSION['token_id'])) {
    header("Location: login.php");
    exit();
}

// Include the database connection logic
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "simulatdb";

// Create a new database connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Fetch and display student information
$tokenID = $_SESSION['token_id'];

// Prepare the SQL query to fetch student information
$sql = "SELECT * FROM Student WHERE token_id = ?";
$stmt = $conn->prepare($sql);

// Bind the token_id parameter
$stmt->bind_param("s", $tokenID);

// Execute the SQL query
$stmt->execute();

// Get the result of the SQL query
$result = $stmt->get_result();

// Check if the query returned any results
if ($result && $result->num_rows > 0) {
    // Fetch the student information
    $row = $result->fetch_assoc();
    // Display student information here as needed
    echo "<h2>Student Information</h2>";
    echo "<p>Student ID: " . $row['student_id'] . "</p>";
    echo "<p>Given Name: " . $row['given_name'] . "</p>";
    echo "<p>Middle Name: " . $row['middle_name'] . "</p>";
    echo "<p>Surname: " . $row['surname'] . "</p>";
    echo "<p>Date of Birth: " . $row['date_of_birth'] . "</p>";
    echo "<p>Gender: " . $row['gender'] . "</p>";
    echo "<p>Enrollment Date: " . $row['enrollment_date'] . "</p>";
} else {
    echo "Error fetching student information.";
}

// Close the database connection
$stmt->close();
$conn->close();

// Add the logout button
echo "<br><a href='logout.php'>Logout</a>";
?>