#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <QProcess>

QT_USE_NAMESPACE

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}


void MainWindow::on_executeSystem_pressed()
{
    QStringList scriptPath(QString ("/home/nana/Desktop/dev/unball/UnBrain/runClient.sh"));
    QString pathShell = "/usr/bin/sh";
    this->unbrain.start(pathShell,scriptPath);

    if(!this->unbrain.waitForStarted()){
        qDebug() << "Failed to start";
        this->unbrain.close();
    }
}

void MainWindow::on_stopSystem_pressed()
{
    this->unbrain.close();
}

