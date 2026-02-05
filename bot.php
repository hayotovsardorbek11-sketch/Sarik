<?php
ini_set('display_errors', true);

// =========================
// Tayyorlangan bot @Sardorbeko008 uchun
// =========================

define('API_KEY', '8501918863:AAE6YCS4j3z0JM9RcpmNXVtk2Kh1qUfABRQ');
$idbot = 'BOT_ID';
$admin = '5775388579';
$owners = array($admin);
$user = "@Sardorbeko008";

$bot=bot('getMe')->result->username;

// ========================= MySQL sozlamalari
define('DB_HOST', 'localhost');      // server manzili
define('DB_USER', 'BAZA_NOMI');      // baza foydalanuvchi
define('DB_PASS', 'BAZA_PAROLI');    // baza paroli
define('DB_NAME', 'BAZA_NOMI');      // baza nomi

$connect = mysqli_connect(DB_HOST, DB_USER, DB_PASS, DB_NAME);
mysqli_set_charset($connect, 'utf8mb4');

if ($connect->connect_error) {
    die("❌ SQL baza ulanmagan: " . $connect->connect_error);
} else {
    echo "✅ SQL baza ulandi!\n";
}

// ========================= Bot funksiyalari
function bot($method,$datas=[]){
    $url = "https://api.telegram.org/bot". API_KEY ."/". $method;
    $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,$url);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
    curl_setopt($ch,CURLOPT_POSTFIELDS,$datas);
    $res = curl_exec($ch);
    if(curl_error($ch)) var_dump(curl_error($ch));
    else return json_decode($res);
}

// ... barcha funksiyalar shu yerga (sendMessage, sendVideo, getChatMember, joinchat va hokazo)

// ========================= JSON fayllar va papkalar yaratish
mkdir("admin");
mkdir("admin/links");
mkdir("admin/zayavka");

// Kino kanali va reklama sozlamalari
file_put_contents("admin/kino.txt", ""); // keyin /panel orqali sozlanadi
file_put_contents("admin/rek.txt", "🎬 Kino bot: %kino% | Admin: %admin%");

// Adminlar ro'yxati
file_put_contents("admin/admins.txt", $admin."\n");

// ========================= MySQL jadval yaratish
mysqli_query($connect,"CREATE TABLE IF NOT EXISTS `data`(
`id` int(20) auto_increment primary key,
`file_name` varchar(256),
`file_id` varchar(256),
`film_name` varchar(256),
`film_date` varchar(256)
)");

mysqli_query($connect,"CREATE TABLE IF NOT EXISTS `settings`(
`id` int(20) auto_increment primary key,
`kino` varchar(256),
`kino2` varchar(256)
)");

mysqli_query($connect,"CREATE TABLE IF NOT EXISTS `user_id`(
`uid` int(20) auto_increment primary key,
`id` varchar(256),
`step` varchar(256),
`ban` varchar(256),
`lastmsg` varchar(256),
`sana` varchar(256)
)");

mysqli_query($connect,"CREATE TABLE IF NOT EXISTS `texts`(
`id` int(20) auto_increment primary key,
`start` varchar(256)
)");

// Default start matni
mysqli_query($connect,"INSERT INTO `texts`(`id`,`start`) VALUES ('1', '".base64_encode("Assalomu alaykum {name}! Botimizga xush kelibsiz!\n\nSoat: {time}")."')");

// ========================= Endi botni ishga tushirish
$update = json_decode(file_get_contents('php://input'));
$message = $update->message;
$callback = $update->callback_query;

// ... Shu yerda barcha logic /panel, obuna tekshirish, kino qo'shish va boshqalar kodlarini qo'shasiz
?>
