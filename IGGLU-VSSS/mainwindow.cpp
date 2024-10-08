#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <QProcess>

QT_USE_NAMESPACE

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , serverIgglu{parent}
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_executeSystem_pressed()
{
    serverIgglu.connectWebSocket(5001);
}

void MainWindow::on_stopSystem_pressed()
{
    serverIgglu.closeWebSocket();
}

void MainWindow::on_sendMessage_clicked()
{
    serverIgglu.sendMessage();
}

