#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QObject>
#include <QProcess>
#include "serverIgglu.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
    QProcess unbrain;
    ServerIgglu serverIgglu;


signals:


private slots:
    void on_executeSystem_pressed();

    void on_stopSystem_pressed();

    void on_sendMessage_clicked();

private:
    Ui::MainWindow *ui;
};
#endif // MAINWINDOW_H
