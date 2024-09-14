#include "mainwindow.h"

#include <QApplication>
#include <QtWebSockets/QtWebSockets>
#include "serverIgglu.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MainWindow w;

    serverIgglu serverIgglu(5001);

    w.show();
    return a.exec();
}
