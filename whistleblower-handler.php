<?php
/**
 * Whistleblower Report Handler
 * Linda Chirwa Attorneys
 *
 * Receives confidential reports and emails them to the designated recipient.
 * Kept separate from contact-handler.php so it can be routed to its own mailbox.
 *
 * Confidentiality rules enforced here:
 *  - No IP address or user-agent is recorded. The form promises that anonymous
 *    reports are not traced, so the server must not trace them either.
 *  - No Reply-To header is set unless the reporter supplied a valid email
 *    address and did not ask to be left uncontacted.
 *  - There is NO fallback to the general inbox. If the dedicated mailbox cannot
 *    be reached, the reporter is told so and given the direct address.
 */

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed.']);
    exit;
}

// ── Configuration ──────────────────────────────────────────────
// Must be a mailbox read only by the designated whistleblower recipient.
$recipientEmail = 'whistleblower@lindachirwaattorneys.co.za';
$subjectPrefix  = '[CONFIDENTIAL - WHISTLEBLOWER]';
$honeypotField  = 'wb_website_url';

// ── Honeypot ───────────────────────────────────────────────────
if (!empty($_POST[$honeypotField])) {
    echo json_encode(['success' => true, 'message' => 'Thank you. Your report has been received.']);
    exit;
}

// ── Helpers ────────────────────────────────────────────────────
// Single-line fields: strip control characters (blocks header injection) and tags.
function wb_line($key, $max = 200) {
    $val = isset($_POST[$key]) && is_string($_POST[$key]) ? $_POST[$key] : '';
    $val = strip_tags($val);
    $val = preg_replace('/[\x00-\x1F\x7F]+/', ' ', $val);
    return mb_substr(trim($val), 0, $max);
}

// ── Collect ────────────────────────────────────────────────────
$organisation  = wb_line('organisation');
$category      = wb_line('category');
$urgency       = wb_line('urgency');
$name          = wb_line('name');
$contact       = wb_line('contact');
$safestContact = wb_line('safest_contact');
$consent       = wb_line('consent');

// Free text: keep line breaks, drop tags and other control characters, cap length.
$description = isset($_POST['description']) && is_string($_POST['description']) ? $_POST['description'] : '';
$description = strip_tags($description);
$description = preg_replace('/[^\P{C}\n\r\t]+/u', '', $description) ?? '';
$description = mb_substr(trim($description), 0, 8000);

// ── Validate ───────────────────────────────────────────────────
$errors = [];
if ($organisation === '') $errors[] = 'Organisation is required.';
if ($category === '')     $errors[] = 'Type of conduct is required.';
if ($description === '')  $errors[] = 'A description of what happened is required.';
if ($consent !== 'yes')   $errors[] = 'Please confirm your declaration.';

if (!empty($errors)) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => implode(' ', $errors)]);
    exit;
}

// ── Build message ──────────────────────────────────────────────
$line = str_repeat('-', 56);

$body  = "CONFIDENTIAL WHISTLEBLOWER REPORT\n";
$body .= str_repeat('=', 56) . "\n\n";
$body .= "Restricted to the designated recipient. Do not forward.\n\n";

$body .= "REPORT DETAILS\n" . $line . "\n";
$body .= "Organisation:    {$organisation}\n";
$body .= "Type of conduct: {$category}\n";
$body .= "Urgency:         " . ($urgency ?: 'Not specified') . "\n\n";

$body .= "REPORTER\n" . $line . "\n";
$body .= "Name:            " . ($name ?: 'ANONYMOUS (no name provided)') . "\n";
$body .= "Contact method:  " . ($contact ?: 'None provided') . "\n";
$body .= "Safest contact:  " . ($safestContact ?: 'Not specified') . "\n\n";

$body .= "DESCRIPTION\n" . $line . "\n";
$body .= $description . "\n\n";

$body .= $line . "\n";
$body .= "Submitted: " . date('Y-m-d H:i') . " (server time)\n";

$subject = mb_encode_mimeheader($subjectPrefix . ' ' . $category, 'UTF-8', 'B', "\r\n");

$headers  = "From: website@lindachirwaattorneys.co.za\r\n";
$headers .= "X-Mailer: LindaChirwaWhistleblower/1.1\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "X-Priority: 1\r\n";

// Reply-To only for a valid email address, and never against the reporter's wishes.
if ($safestContact !== 'Do not contact me' && filter_var($contact, FILTER_VALIDATE_EMAIL)) {
    $headers .= "Reply-To: {$contact}\r\n";
}

// ── Send ───────────────────────────────────────────────────────
$sent = @mail($recipientEmail, $subject, $body, rtrim($headers));

if ($sent) {
    echo json_encode([
        'success' => true,
        'message' => 'Thank you. Your report has been received confidentially. If you provided contact details, we will be in touch via your preferred method.'
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'We could not submit your report at this time. Please email whistleblower@lindachirwaattorneys.co.za directly, marking your email CONFIDENTIAL - WHISTLEBLOWER.'
    ]);
}
